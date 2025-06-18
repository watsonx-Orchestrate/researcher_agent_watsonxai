import json

import requests


def test_chat_completions_sync():
    """동기 모드로 /chat/completions 엔드포인트 테스트"""
    url = "https://load-wxai-agent.1wpveihz0wfq.us-south.codeengine.appdomain.cloud/chat/completions"

    # 테스트 요청 데이터
    data = {
        "model": "test-model",
        "messages": [
            {"role": "user", "content": "안녕하세요! 간단한 질문이 있습니다."}
        ],
        "stream": False,
        "context": {},
        "extra_body": {"thread_id": "test-thread-123"},
    }

    # 헤더 설정
    headers = {"Content-Type": "application/json", "X-IBM-THREAD-ID": "test-thread-123"}

    try:
        print("=== 동기 모드 테스트 ===")
        print(f"요청 URL: {url}")
        print(f"요청 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")

        response = requests.post(url, json=data, headers=headers)

        print(f"상태 코드: {response.status_code}")
        print(f"응답 헤더: {dict(response.headers)}")

        if response.status_code == 200:
            response_data = response.json()
            print(
                f"응답 데이터: {json.dumps(response_data, indent=2, ensure_ascii=False)}"
            )
        else:
            print(f"오류 응답: {response.text}")

    except requests.exceptions.ConnectionError:
        print("연결 오류: 서버가 실행중인지 확인하세요. (uvicorn app:app --reload)")
    except Exception as e:
        print(f"테스트 실행 중 오류 발생: {e}")


def test_chat_completions_stream():
    """스트림 모드로 /chat/completions 엔드포인트 테스트"""
    url = "https://load-wxai-agent.1wpveihz0wfq.us-south.codeengine.appdomain.cloud/chat/completions"

    # 테스트 요청 데이터 (스트림 모드)
    data = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "스트림 모드로 응답해주세요."}],
        "stream": True,
        "context": {},
        "extra_body": {"thread_id": "test-stream-123"},
    }

    # 헤더 설정
    headers = {"Content-Type": "application/json", "X-IBM-THREAD-ID": "test-stream-123"}

    try:
        print("\n=== 스트림 모드 테스트 ===")
        print(f"요청 URL: {url}")
        print(f"요청 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")

        response = requests.post(url, json=data, headers=headers, stream=True)

        print(f"상태 코드: {response.status_code}")

        if response.status_code == 200:
            print("스트림 응답:")
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    print(f"  {decoded_line}")
        else:
            print(f"오류 응답: {response.text}")

    except requests.exceptions.ConnectionError:
        print("연결 오류: 서버가 실행중인지 확인하세요. (uvicorn app:app --reload)")
    except Exception as e:
        print(f"테스트 실행 중 오류 발생: {e}")


def test_chat_completions_with_conversation():
    """대화 형태로 /chat/completions 엔드포인트 테스트"""
    url = "https://load-wxai-agent.1wpveihz0wfq.us-south.codeengine.appdomain.cloud/chat/completions"

    # 대화 형태의 테스트 데이터
    data = {
        "model": "test-model",
        "messages": [
            {"role": "system", "content": "당신은 도움이 되는 AI 어시스턴트입니다."},
            {
                "role": "user",
                "content": "Python에서 FastAPI를 사용하는 방법을 알려주세요.",
            },
            {"role": "assistant", "content": "FastAPI는 Python의 웹 프레임워크입니다."},
            {"role": "user", "content": "더 자세한 예시를 보여주세요."},
        ],
        "stream": False,
        "context": {"session_id": "conversation-test"},
    }

    headers = {"Content-Type": "application/json"}

    try:
        print("\n=== 대화 형태 테스트 ===")
        print(f"요청 URL: {url}")
        print(f"메시지 개수: {len(data['messages'])}")

        response = requests.post(url, json=data, headers=headers)

        print(f"상태 코드: {response.status_code}")

        if response.status_code == 200:
            response_data = response.json()
            print(f"응답: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        else:
            print(f"오류 응답: {response.text}")

    except requests.exceptions.ConnectionError:
        print("연결 오류: 서버가 실행중인지 확인하세요. (uvicorn app:app --reload)")
    except Exception as e:
        print(f"테스트 실행 중 오류 발생: {e}")


if __name__ == "__main__":
    print("=== WatsonX AI Agent 엔드포인트 테스트 ===")
    print("서버를 먼저 실행하세요: uvicorn app:app --reload")
    print()

    # 각 테스트 실행
    test_chat_completions_sync()
    test_chat_completions_stream()
    test_chat_completions_with_conversation()

    print("\n테스트 완료!")
