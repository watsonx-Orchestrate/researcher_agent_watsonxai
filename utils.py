import json
import logging
import os
import time
import traceback
import uuid
from typing import List

import requests
from ibm_watsonx_ai import APIClient
from models import Message

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

sessions = {}


def _get_access_token(APIKEY):
    api_key = APIKEY
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "accept": "application/json",
    }
    data = {"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key}
    session = sessions.get(api_key, None)
    if session == None or time.time() - session["expiry"] > 3500:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            token_data = json.loads(response.text)
            token = token_data["access_token"]
            sessions[api_key] = {"token": token, "expiry": time.time()}
            logger.info("Retrieved new token")
            return token
        else:
            raise Exception("Failed to get access token")
    else:
        logger.info("Using old token")
        return session["token"]


def _get_wxai_client(SPACE_ID, APIKEY, WATSONX_URL):
    credentials = {
        "url": WATSONX_URL,
        "token": _get_access_token(APIKEY),
    }
    return APIClient(
        credentials,
        space_id=SPACE_ID,
    )


def get_llm_sync(
    DEPLOYMENT_ID,
    SPACE_ID,
    APIKEY,
    WATSONX_URL,
    messages,
):
    logger.info("wx.ai deployment Synchronous call")

    client = _get_wxai_client(SPACE_ID, APIKEY, WATSONX_URL)
    payload = {
        "messages": [
            m.model_dump() for m in messages if m.role != "system" and m.role != "tool"
        ]
    }
    logger.info(f"Calling AI service with payload: {payload}")
    result = client.deployments.run_ai_service(
        DEPLOYMENT_ID,
        payload,
    )
    if "error" in result:
        raise RuntimeError(f"Got an error from wx.ai AI service: {result['error']}")

    logger.info(f"Response: {result}")
    return [Message(**c["message"]) for c in result["choices"]]


def format_resp(struct):
    return "data: " + json.dumps(struct) + "\n\n"


def _json_loads_no_fail(json_string: str):
    try:
        return json.loads(json_string)
    except:
        return {}


async def get_llm_stream(
    DEPLOYMENT_ID,
    SPACE_ID,
    APIKEY,
    WATSONX_URL,
    messages,
    thread_id,
):
    client = _get_wxai_client(SPACE_ID, APIKEY, WATSONX_URL)
    payload = {
        "messages": [
            m.model_dump() for m in messages if m.role != "system" and m.role != "tool"
        ]
    }
    logger.info(f"Calling AI service with payload: {payload}")
    try:
        for chunk in client.deployments.run_ai_service_stream(DEPLOYMENT_ID, payload):
            logger.info(f"Received chunk: {chunk}")
            try:
                delta = json.loads(chunk)["choices"][0]["delta"]
            except:
                warning_msg = "It's likely that you are using an old AI service built with a wrong/obsolete response schema, please deploy a new AI service."
                logger.warning(warning_msg)
                raise RuntimeError(warning_msg)

            current_timestamp = int(time.time())
            delta_id = str(uuid.uuid4())
            struct = {
                "id": delta_id,
                "object": "thread.run.step.delta",
                "created": current_timestamp,
                "thread_id": thread_id,
                "model": "wx.ai AI service",
            }
            if delta["role"] == "assistant" and "tool_calls" in delta:
                struct["choices"] = [
                    {
                        "delta": {
                            "role": "assistant",
                            "step_details": {
                                "type": "tool_calls",
                                "tool_calls": [
                                    {
                                        "name": tool_call["function"]["name"],
                                        "args": _json_loads_no_fail(
                                            tool_call["function"]["arguments"]
                                        ),
                                        "id": tool_call["id"],
                                    }
                                    for tool_call in delta["tool_calls"]
                                ],
                            },
                        }
                    }
                ]
            elif delta["role"] == "tool":
                struct["choices"] = [
                    {
                        "delta": {
                            "role": "assistant",
                            "step_details": {
                                "type": "tool_response",
                                "name": delta["name"],
                                "tool_call_id": delta["tool_call_id"],
                                "content": delta["content"],
                            },
                        }
                    }
                ]
            elif delta["role"] == "assistant" and "content" in delta:
                struct["choices"] = [{"delta": delta}]
            else:
                # should not happen
                logger.warning("Enable to parse delta: " + delta)
            event_content = format_resp(struct)
            logger.info("Sending event content: " + event_content)
            yield event_content
    except Exception as e:
        logger.error(f"Exception {str(e)}")
        traceback.print_exc()
        yield f"Error: {str(e)}\n"
