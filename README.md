# researcher_agent_watsonxai
watsonx.ai에서 agent lab을 통하여 에이전트를 빌드하고 space에 배포한 서비스임.

```curl
curl -X POST "https://research-agent-app.1wrbgjmhze46.us-south.codeengine.appdomain.cloud/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      { "role": "user", "content": "IBM 최신 뉴스는?" }
    ],
    "stream": false
  }'
```

로컬에서 확인.

```bash
pip install fastapi uvicorn
```
```bash
uvicorn app:app --host 0.0.0.0 --port 8080 --reload

```
```bash
curl -X POST "http://127.0.0.1:8080/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      { "role": "user", "content": "IBM 최신 뉴스는?" }
    ],
    "stream": false
  }'
```
