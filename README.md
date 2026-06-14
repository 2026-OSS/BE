# AI Picture Book Backend

시각장애 아동을 위한 AI 그림책 보조 서비스의 백엔드입니다.

FastAPI를 기반으로 API 서버를 구성합니다.

## 실행 방법

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

로컬 서버 주소는 기본적으로 `http://127.0.0.1:8000`입니다.

## API

### Health Check

`GET /health`
