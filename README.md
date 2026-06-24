# Fingertips Backend

시각장애 아동을 위한 촉각형 그림책 보조 서비스 Fingertips의 백엔드 레포지토리입니다.

본 레포지토리는 프론트엔드에서 전달받은 카메라 프레임을 AI 서버로 전달하고, 객체 탐지·페이지 분류·손끝 위치 분석 결과를 바탕으로 적절한 안내 문장을 생성하는 백엔드 애플리케이션을 관리합니다.

또한 손끝-객체 매칭, 페이지 기반 설명 조회, OpenAI TTS 기반 음성 안내 기능을 함께 제공합니다.

## System Overview

Fingertips는 시각장애 아동이 촉각형 그림책과 촉각 교구를 손끝으로 탐색하면, AI가 현재 페이지와 객체를 인식하고 해당 설명을 음성으로 안내하는 시스템입니다.

본 레포지토리는 전체 시스템 중 Backend 영역을 담당하며, Frontend와 AI Server 사이에서 요청을 중계하고 최종 상호작용 응답을 생성합니다.

### Backend Role

Frontend
    ↓
Backend (FastAPI)
    ↓
AI Server (YOLO + Page Classifier)
    ↓
Backend
    ↓
Frontend

### Interaction Pipeline


카메라 프레임
    ↓
AI 서버 추론 요청
    ↓
객체 탐지 / 페이지 분류 / 손끝 위치 분석
    ↓
손끝-객체 매칭
    ↓
설명 조회
    ↓
음성 변환(TTS)


## Repository Structure

- `app/api` : FastAPI 라우터 및 API 엔드포인트
- `app/core` : 환경 변수 및 설정 로딩
- `app/data` : 페이지·객체별 설명 문장 JSON
- `app/models` : 요청/응답 스키마 정의
- `app/services` : AI 서버 호출, 매칭 로직, 설명 조회, TTS 처리
- `tests` : 설정, 설명, 매칭, 응답, TTS 관련 테스트 코드

## Tech Stack

- Language: Python
- Framework: FastAPI
- ASGI Server: Uvicorn
- HTTP Client: httpx
- Environment: python-dotenv
- File Upload: python-multipart
- TTS: OpenAI TTS API
- Data Format: JSON

---

# 사전 준비

## 1. 필수 설치 항목

- Python 3 환경
- `pip`
- AI 서버 실행 환경
- OpenAI API Key (`/api/tts` 사용 시 필요)

## 2. 설치 라이브러리

`requirements.txt`에 포함된 주요 라이브러리는 다음과 같습니다.

- FastAPI
- Uvicorn
- httpx
- python-multipart
- python-dotenv
- numpy
- pillow

## 3. 실행 전 확인 사항

- AI 서버 기본 주소는 `http://127.0.0.1:8001` 입니다.
- OpenAI API Key가 없으면 `/api/tts` 음성 생성 기능은 동작하지 않습니다.
- AI 서버가 실행되지 않은 상태에서는 `/api/interaction/detect` 호출 시 오류가 발생합니다.
- AI 서버 없이 백엔드 로직만 확인하려면 `/api/interaction/mock` API를 사용할 수 있습니다.

---

# 실행 방법

가상환경 생성 후 필요한 라이브러리를 설치합니다.

```
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

환경 변수를 설정합니다.

`cp .env.example .env`

필요한 경우 `.env`에서 다음 값을 수정합니다.

```
AI_SERVER_URL=http://127.0.0.1:8001
OPENAI_API_KEY=your_openai_api_key
```

서버를 실행합니다.

`uvicorn app.main:app --reload`

기본 실행 주소는 `http://127.0.0.1:8000` 입니다.

## 권장 실행 순서

1. AI 서버를 먼저 실행합니다.
2. Backend 서버를 실행합니다.
3. 프론트엔드 또는 API 테스트 도구에서 Backend API를 호출합니다.
4. TTS까지 확인하려면 `.env`에 `OPENAI_API_KEY`를 설정합니다.

## 빠른 확인 순서

1. 서버 상태 확인

`curl http://127.0.0.1:8000/health`

2. AI 서버 없이 Mock API 테스트

```
curl -X POST "http://127.0.0.1:8000/api/interaction/mock?voiceType=child" \
  -H "Content-Type: application/json" \
  -d '{
    "page": { "label": "page2", "confidence": 0.96 },
    "objects": [
      { "label": "book_monkey", "confidence": 0.95, "bbox": [120, 85, 300, 410] }
    ],
    "finger": { "x": 210, "y": 180 }
  }'
```

3. OpenAI TTS 테스트

```
curl -X POST "http://127.0.0.1:8000/api/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "꼬마 원숭이가 코코넛 화분에 꽃을 심고 있어.",
    "voiceType": "child"
  }'
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

```
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

```
page2 + book_monkey
→ "꼬마 원숭이는 코코넛을 주워 반으로 쪼갠 다음 그 안에 흙을 넣고 꽃을 심었어요."
```

---

## 4. 음성 생성(TTS)

OpenAI TTS를 이용하여 설명 문장을 음성으로 변환합니다.

지원 음성 유형

- `child` : 어린이 음성
- `mom` : 부모 음성
- `dad` : 아버지 음성

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

`frame: image file`

예시

```
curl -X POST "http://127.0.0.1:8000/api/interaction/detect" \
  -F "frame=@sample.jpg" \
  -F "voiceType=child"
```

Response

```
{
  "matched": true,
  "page": "page2",
  "object": "book_monkey",
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
  },
  "description": "꼬마 원숭이는 코코넛을 주워 반으로 쪼갠 다음 그 안에 흙을 넣고 꽃을 심었어요.",
  "ttsText": "꼬마 원숭이는 코코넛을 주워 반으로 쪼갠 다음 그 안에 흙을 넣고 꽃을 심었어요.",
  "message": "대상을 찾았습니다.",
  "distance": 0.0
}
```

---

## Mock Interaction

### POST /api/interaction/mock

AI 서버 없이 Backend 로직을 테스트할 수 있습니다.

Request

```
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

```
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

```
{
  "text": "꼬마 원숭이가 코코넛 화분에 꽃을 심고 있어.",
  "voiceType": "child"
}
```

Response

`mp3 audio binary`

---

# AI 응답 형식

Backend는 AI 서버로부터 다음 형식의 응답을 받습니다.

```
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

```
{
  "label": "page2",
  "confidence": 0.96
}
```

## Objects

탐지된 객체 목록

```
{
  "label": "book_monkey",
  "confidence": 0.95,
  "bbox": [120, 85, 300, 410]
}
```

Bounding Box 형식

`[x1, y1, x2, y2]`

## Finger

손끝 좌표

```
{
  "x": 210,
  "y": 180
}
```

---

# 테스트 방법

## 단위 테스트 실행

`pytest`

특정 테스트만 실행하려면 예시는 다음과 같습니다.

- `pytest tests/test_interaction_response.py`
- `pytest tests/test_tts_client.py`

## 테스트 없이 기능만 빠르게 확인하는 방법

- AI 서버 연결 확인: `GET /health`
- 매칭 로직 확인: `POST /api/interaction/mock`
- 음성 생성 확인: `POST /api/tts`

---

# 문제 해결

## 1. AI 서버 연동 실패

- AI 서버가 실행 중인지 확인합니다.
- `.env`의 `AI_SERVER_URL` 값이 올바른지 확인합니다.

## 2. TTS 생성 실패

- `.env`에 `OPENAI_API_KEY`가 설정되어 있는지 확인합니다.
- OpenAI 사용량 또는 네트워크 상태를 확인합니다.

## 3. 페이지 분류기가 동작하지 않음

- `PAGE_CLASSIFIER_ENABLED=true` 설정 여부를 확인합니다.
- 모델 파일 경로와 클래스 파일 경로가 올바른지 확인합니다.

## 4. AI 서버 없이 로직만 확인하고 싶을 때

- `/api/interaction/mock` API를 사용합니다.

---

# 프로젝트 목적

본 프로젝트는 시각장애 아동이 촉각 그림책을 보다 능동적으로 탐색할 수 있도록 지원하는 것을 목표로 한다.

기존 오디오북 방식의 일방향 설명을 보완하기 위해, 사용자가 직접 손끝으로 가리킨 대상에 대해 상황에 맞는 설명과 음성 안내를 제공한다. 이는 아동의 자율적 탐색 경험과 학습 몰입도를 향상시키기 위한 AI 기반 보조 서비스이다.
