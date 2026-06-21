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

`AI_SERVER_URL`은 AI 서버 기본 주소입니다. 기본값은 `http://127.0.0.1:8001`이고, 예시로 `http://127.0.0.1:9000`처럼 바꿔서 사용할 수 있습니다.

`AI_PREDICT_PATH`는 AI 예측 API 경로입니다. 기본값은 `/predict`입니다.

`AI_FRAME_FIELD_NAME`은 AI 서버로 보낼 multipart 필드명입니다. 기본값은 `frame`입니다.

`OPENAI_API_KEY`는 OpenAI TTS 호출에 사용할 API 키입니다. OpenAI 음성 생성을 쓸 때 반드시 필요합니다.

`OPENAI_API_BASE_URL`은 OpenAI API 기본 주소입니다. 기본값은 `https://api.openai.com/v1`입니다.

`OPENAI_TTS_MODEL`은 음성 생성 모델입니다. 기본값은 `gpt-4o-mini-tts`입니다.

`OPENAI_TTS_RESPONSE_FORMAT`은 음성 응답 포맷입니다. 기본값은 `mp3`입니다. 지연을 조금 더 줄이고 싶으면 `wav`나 `pcm`으로 바꿔볼 수 있습니다.

`OPENAI_TTS_TIMEOUT`은 OpenAI TTS 요청 제한 시간입니다. 기본값은 `30`초입니다.

`PAGE_CONFIDENCE_THRESHOLD`는 설명 조회에 사용할 페이지 confidence 임계값입니다. 기본값은 `0.75`입니다. 이 값보다 낮으면 AI가 반환한 페이지 라벨은 응답에 남기되, 설명은 페이지 인식 fallback 문구를 사용합니다.

`PAGE_CLASSIFIER_ENABLED`는 백엔드 내장 페이지 분류기 사용 여부입니다. 기본값은 `false`입니다. AI 서버가 페이지 안정화 결과를 반환하므로 기본 동작은 AI 서버의 페이지 결과를 그대로 사용합니다. `true`로 켜면 백엔드 내장 분류기가 confidence 기준을 넘을 때 AI 서버의 페이지 결과를 교체합니다.

`PAGE_CLASSIFIER_CONFIDENCE_THRESHOLD`는 내장 페이지 분류기가 AI 서버의 페이지 결과를 교체할 때 사용할 confidence 임계값입니다. 기본값은 `0.75`입니다.

`PAGE_CLASSIFIER_MODEL_PATH`와 `PAGE_CLASSIFIER_CLASS_NAMES_PATH`로 내장 페이지 분류 모델과 클래스명 파일 위치를 바꿀 수 있습니다. 기본 모델은 `app/data/page_classifier/page_classifier_mobilenetv2.keras`, 클래스명은 `app/data/page_classifier/class_names.json`입니다.

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

### TTS Audio

`POST /api/tts`

OpenAI TTS로 음성을 생성해서 오디오 바이너리로 반환합니다.

요청 예시:

```json
{
  "text": "꼬마 원숭이가 코코넛 화분에 꽃을 심고 있어.",
  "voiceType": "child"
}
```

`voiceType`은 `child`, `mom`, `dad` 중 하나를 사용합니다.

## AI 응답 기준

AI 응답은 `page`, `objects`, `finger` 구조를 기준으로 합니다.

`page`에는 현재 페이지 라벨과 confidence가 들어갑니다.

`objects`에는 객체 라벨, confidence, bbox가 들어갑니다. bbox는 `[x1, y1, x2, y2]` 순서입니다. 객체 라벨 필드는 `label`, `class`, `class_name`을 모두 받을 수 있습니다.

`finger`에는 손끝 좌표 `x`, `y`가 들어갑니다.
