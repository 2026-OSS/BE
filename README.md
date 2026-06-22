# Fingertips Backend

시각장애 아동을 위한 AI 그림책 보조 서비스 **Fingertips**의 Backend 프로젝트입니다.

Backend는 프론트엔드에서 전달받은 카메라 프레임을 AI 서버로 전달하고, 객체 탐지·페이지 분류·손끝 위치 분석 결과를 바탕으로 적절한 안내 문장을 생성합니다.

또한 OpenAI TTS를 활용하여 안내 문장을 음성으로 변환하는 기능을 제공합니다.

## 시스템 구조

```text
Frontend
    ↓
Backend (FastAPI)
    ↓
AI Server (YOLO + Page Classifier)
    ↓
Backend
    ↓
Frontend
```

```text
카메라 프레임
    ↓
객체 탐지
    ↓
손끝 위치 추적
    ↓
대상 매칭
    ↓
설명 생성
    ↓
음성 변환(TTS)
```

---

# 실행 방법

가상환경 생성 후 필요한 라이브러리를 설치합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

환경 변수를 설정합니다.

```bash
cp .env.example .env
```

서버를 실행합니다.

```bash
uvicorn app.main:app --reload
```

기본 실행 주소는 다음과 같습니다.

```text
http://127.0.0.1:8000
```

---

# 주요 기능

## 1. AI 서버 연동

프론트엔드로부터 전달받은 카메라 프레임을 AI 서버로 전달합니다.

AI 서버는 다음 정보를 반환합니다.

* 페이지 정보
* 객체 탐지 결과
* 손끝 좌표

Backend는 해당 정보를 기반으로 사용자가 가리키는 대상을 판별합니다.

---

## 2. 손끝-객체 매칭

객체 중심점과 손끝 좌표 간 거리를 계산하여 사용자가 가리키는 대상을 결정합니다.

```text
Finger
   ↓
Distance Calculation
   ↓
Nearest Object
   ↓
Description Lookup
```

---

## 3. 페이지 기반 설명 생성

현재 페이지와 탐지된 객체를 기준으로 사전에 정의된 설명 문장을 조회합니다.

예시

```text
page2 + book_monkey
→ "꼬마 원숭이는 코코넛을 주워 반으로 쪼갠 다음 그 안에 흙을 넣고 꽃을 심었어요."
```

---

## 4. 음성 생성(TTS)

OpenAI TTS를 이용하여 설명 문장을 음성으로 변환합니다.

지원 음성 유형

| Type  | Description |
| ----- | ----------- |
| child | 어린이 음성      |
| mom   | 부모 음성       |
| dad   | 아버지 음성      |

---

# 환경 변수

프로젝트는 `.env` 파일을 통해 설정을 관리합니다.

## AI Server

| 변수명                 | 기본값                                            | 설명        |
| ------------------- | ---------------------------------------------- | --------- |
| AI_SERVER_URL       | [http://127.0.0.1:8001](http://127.0.0.1:8001) | AI 서버 주소  |
| AI_PREDICT_PATH     | /predict                                       | 예측 API 경로 |
| AI_FRAME_FIELD_NAME | frame                                          | 이미지 필드명   |

## OpenAI TTS

| 변수명                        | 기본값                                                    | 설명             |
| -------------------------- | ------------------------------------------------------ | -------------- |
| OPENAI_API_KEY             | -                                                      | OpenAI API Key |
| OPENAI_API_BASE_URL        | [https://api.openai.com/v1](https://api.openai.com/v1) | API 주소         |
| OPENAI_TTS_MODEL           | gpt-4o-mini-tts                                        | 음성 생성 모델       |
| OPENAI_TTS_RESPONSE_FORMAT | mp3                                                    | 출력 포맷          |
| OPENAI_TTS_TIMEOUT         | 30                                                     | 요청 제한 시간(초)    |

## Page Classifier

| 변수명                                  | 기본값   | 설명           |
| ------------------------------------ | ----- | ------------ |
| PAGE_CLASSIFIER_ENABLED              | false | 내장 분류기 사용 여부 |
| PAGE_CONFIDENCE_THRESHOLD            | 0.75  | 페이지 신뢰도 기준   |
| PAGE_CLASSIFIER_CONFIDENCE_THRESHOLD | 0.75  | 교체 기준 신뢰도    |
| PAGE_CLASSIFIER_MODEL_PATH           | 기본 경로 | 모델 파일 경로     |
| PAGE_CLASSIFIER_CLASS_NAMES_PATH     | 기본 경로 | 클래스 파일 경로    |

## Object Matching

| 변수명                      | 기본값 | 설명           |
| ------------------------ | --- | ------------ |
| MATCH_DISTANCE_THRESHOLD | 80  | 손끝-객체 거리 임계값 |

---

# API

## Health Check

### GET /health

서버 상태를 확인합니다.

---

## Interaction Detect

### POST /api/interaction/detect

카메라 프레임을 전달하여 AI 분석 결과를 반환합니다.

Request

```text
frame: image file
```

---

## Mock Interaction

### POST /api/interaction/mock

AI 서버 없이 Backend 로직을 테스트할 수 있습니다.

Request

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

Response

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

---

## TTS Audio

### POST /api/tts

설명 문장을 음성으로 변환합니다.

Request

```json
{
  "text": "꼬마 원숭이가 코코넛 화분에 꽃을 심고 있어.",
  "voiceType": "child"
}
```

---

# AI 응답 형식

Backend는 AI 서버로부터 다음 형식의 응답을 받습니다.

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

## Page

현재 그림책 페이지 정보

```json
{
  "label": "page2",
  "confidence": 0.96
}
```

## Objects

탐지된 객체 목록

```json
{
  "label": "book_monkey",
  "confidence": 0.95,
  "bbox": [120, 85, 300, 410]
}
```

Bounding Box 형식

```text
[x1, y1, x2, y2]
```

## Finger

손끝 좌표

```json
{
  "x": 210,
  "y": 180
}
```

---

# 프로젝트 목적

본 프로젝트는 시각장애 아동이 촉각 그림책을 보다 능동적으로 탐색할 수 있도록 지원하는 것을 목표로 한다.

기존 오디오북 방식의 일방향 설명을 보완하기 위해, 사용자가 직접 손끝으로 가리킨 대상에 대해 상황에 맞는 설명과 음성 안내를 제공한다. 이는 아동의 자율적 탐색 경험과 학습 몰입도를 향상시키기 위한 AI 기반 보조 서비스이다.
