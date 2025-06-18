import logging
import os
import time
import uuid
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse, StreamingResponse
from models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    Choice,
    MessageResponse,
)
from utils import get_llm_stream, get_llm_sync

load_dotenv()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
console_hanlder = logging.StreamHandler()
console_hanlder.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_hanlder.setFormatter(formatter)
logger.addHandler(console_hanlder)

app = FastAPI()


@app.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    X_IBM_THREAD_ID: Optional[str] = Header(
        None,
        alias="X-IBM-THREAD-ID",
        description="Optional header to specify the thread ID",
    ),
):
    logger.info(
        f"Received POST /chat/completions ChatCompletionRequest: {request.json()}"
    )

    thread_id = ""
    if X_IBM_THREAD_ID:
        thread_id = X_IBM_THREAD_ID
    if request.extra_body and request.extra_body.thread_id:
        thread_id = request.extra_body.thread_id
    logger.info("thread_id: " + thread_id)

    if request.stream:
        return StreamingResponse(
            get_llm_stream(
                os.getenv("DEPLOYMENT_ID"),
                os.getenv("SPACE_ID"),
                os.getenv("APIKEY"),
                os.getenv("WATSONX_URL"),
                request.messages,
                thread_id,
            ),
            media_type="text/event-stream",
        )
    else:
        all_messages = get_llm_sync(
            os.getenv("DEPLOYMENT_ID"),
            os.getenv("SPACE_ID"),
            os.getenv("APIKEY"),
            os.getenv("WATSONX_URL"),
            request.messages,
        )

        response = ChatCompletionResponse(
            id=str(uuid.uuid4()),
            object="chat.completion",
            created=int(time.time()),
            model="wx.ai AI service",
            choices=[
                Choice(
                    index=0,
                    message=MessageResponse(
                        role="assistant", content=all_messages[-1].content
                    ),
                    finish_reason="stop",
                )
            ],
        )
        return JSONResponse(content=response.dict())
