# AI Picture Book Backend

시각장애 아동을 위한 AI 그림책 보조 서비스의 백엔드입니다.

카메라 프레임을 AI 서버에 보내고, 분석 결과에 맞는 안내 문장을 반환합니다.

## 실행 방법

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

로컬 서버 주소는 기본적으로 `http://127.0.0.1:8000`입니다.

## 환경 변수

`AI_SERVER_URL`은 AI 서버 기본 주소입니다. 예시는 `http://127.0.0.1:9000`입니다.

`AI_PREDICT_PATH`는 AI 예측 API 경로입니다. 기본값은 `/predict`입니다.

`AI_FRAME_FIELD_NAME`은 AI 서버로 보낼 multipart 필드명입니다. 기본값은 `frame`입니다.

`MATCH_DISTANCE_THRESHOLD`는 손끝과 객체 중심점 거리 임계값입니다. 기본값은 `80`입니다.

## API

### Health Check

`GET /health`

### Interaction Detect

`POST /api/interaction/detect`

프론트엔드에서 전달한 카메라 프레임을 `multipart/form-data`의 `frame` 필드로 받습니다.

```text
frame: camera frame image
```

### Mock Interaction

`POST /api/interaction/mock`

AI 서버 없이 백엔드 응답을 확인할 때 사용합니다.

요청 예시:

```json
{
  "page": {
    "label": "page2",
    "confidence": 0.96
  },
  "objects": [
    {
      "label": "book_monkey",
      "confidence": 0.95,
      "bbox": [120, 85, 300, 410]
    }
  ],
  "finger": {
    "x": 210,
    "y": 180
  }
}
```

응답 예시:

```json
{
  "matched": true,
  "page": "page2",
  "object": "book_monkey",
  "description": "꼬마 원숭이는 코코넛을 주워 반으로 쪼갠 다음 그 안에 흙을 넣고 꽃을 심었어요.",
  "ttsText": "꼬마 원숭이는 코코넛을 주워 반으로 쪼갠 다음 그 안에 흙을 넣고 꽃을 심었어요.",
  "message": "대상을 찾았습니다.",
  "distance": 0.0
}
```

## AI 응답 기준

AI 응답은 `page`, `objects`, `finger` 구조를 기준으로 합니다.

`page`에는 현재 페이지 라벨과 confidence가 들어갑니다.

`objects`에는 객체 라벨, confidence, bbox가 들어갑니다. bbox는 `[x1, y1, x2, y2]` 순서입니다. 객체 라벨 필드는 `label`, `class`, `class_name`을 모두 받을 수 있습니다.

`finger`에는 손끝 좌표 `x`, `y`가 들어갑니다.
