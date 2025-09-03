# 주가 계산 챗봇

LangGraph와 Streamlit을 사용한 비동기 주가 계산 챗봇입니다.

## 🎯 핵심 기능

- ✅ **토큰 단위 스트리밍**: 실시간 문자별 응답
- ✅ **멀티턴 대화**: LangGraph checkpointer 활용
- ✅ **실시간 주가**: yfinance API 통합
- ✅ **수학 계산**: numexpr 기반 계산 도구
- ✅ **Streamlit UI**: 사용자 친화적 웹 인터페이스
- ✅ **완전 비동기**: 모든 처리가 비동기로 구현

## 📁 디렉토리 구조

```
Assignment1/
├── frontend/            # 🎨 사용자 인터페이스
│   └── streamlit_app.py # Streamlit 메인 앱
├── backend/             # 🚀 FastAPI 서버 (선택사항)
│   └── main.py          # API 서버
├── ai/                  # 🤖 AI 에이전트
│   ├── agent/
│   │   └── stock_agent.py    # LangGraph 에이전트
│   └── tools/
│       ├── stock_price.py    # 주가 조회 도구
│       ├── calculator.py     # 계산 도구
│       └── stock_tools.py    # 도구 통합
├── test/                # 🧪 테스트
│   └── test_stock_agent.py   # pytest 테스트 (multi-turn 포함)
├── requirements.txt     # 📦 의존성
├── .env                 # 🔑 환경변수 (OpenAI API 키)
└── README.md
```

## 🚀 설치 및 실행

### 1. 가상환경 설정
```bash
conda create -n stock-chatbot python=3.9
conda activate stock-chatbot
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정
`.env` 파일을 생성하고 OpenAI API 키를 설정하세요:
```bash
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

## 🚀 실행 방법 (두 가지 옵션)

### 옵션 1: Streamlit만 실행 (권장 ⭐)
```bash
streamlit run frontend/streamlit_app.py
```
- **브라우저 자동 열림**: http://localhost:8501
- **AI 에이전트 직접 연동**: FastAPI 서버 불필요
- **완전한 기능**: 토큰 스트리밍, Multi-turn 대화 모두 지원

### 옵션 2: FastAPI + Streamlit 함께 실행
```bash
# 터미널 1: FastAPI 서버 실행
cd backend && python main.py

# 터미널 2: Streamlit 실행  
streamlit run frontend/streamlit_app.py
```
- **FastAPI 서버**: http://localhost:8000 (API 엔드포인트)
- **Streamlit 앱**: http://localhost:8501 (사용자 인터페이스)
- **API 테스트**: curl로 직접 API 호출 가능

## 📋 **어떤 방법을 선택해야 할까요?**

| 옵션 | 장점 | 용도 |
|------|------|------|
| **Streamlit만** | 간단, 빠른 시작 | 일반 사용자, 데모 |
| **FastAPI + Streamlit** | API 테스트 가능 | 개발자, API 활용 |

## 🎨 Streamlit 앱 특징

### 사용자 인터페이스
- **💬 실시간 채팅**: 메시지 입력과 즉시 응답
- **⚡ 토큰 스트리밍**: 실제 타이핑하듯 문자별 출력
- **📜 대화 히스토리**: 이전 대화 내용 유지 및 표시
- **⚙️ 사이드바**: 설정 및 기능 안내

### 기술적 특징
- **🔗 직접 연동**: FastAPI 없이 AI 에이전트 직접 사용
- **🔄 비동기 처리**: asyncio를 통한 스트리밍 응답
- **💾 세션 관리**: Streamlit 세션으로 대화 유지
- **🛡️ 에러 처리**: 친화적인 오류 메시지

## 💡 사용 예시

### 1. 주가 조회
```
👤 "AAPL 주가 알려줘"
🤖 "Apple Inc. (AAPL)의 현재 주가는 $175.43입니다."
```

### 2. 계산
```
👤 "100 * 1.5는?"
🤖 "100 * 1.5 = 150.0입니다."
```

### 3. 복합 질문
```
👤 "엔비디아 5주랑 아마존 8주를 두명이 돈을 모아 사려고 하는데, 각자 얼마나 돈 챙겨야 해?"
🤖 "NVDA 5주: $4,376.40, AMZN 8주: $1,166.88
총 $5,543.28이므로 각자 $2,771.64씩 준비하시면 됩니다."
```

## 📡 API 엔드포인트 (FastAPI 서버 사용 시)

### POST /chat/stream
```bash
curl -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"message": "AAPL 주가 알려줘", "thread_id": "user_123"}'
```

### POST /clear
```bash
curl -X POST "http://localhost:8000/clear" \
  -H "Content-Type: application/json" \
  -d '{"thread_id": "user_123"}'
```

### GET /health
```bash
curl http://localhost:8000/health
```

## 🛠️ 기술 스택

| 구분 | 기술 | 설명 |
|------|------|------|
| **Frontend** | Streamlit | 사용자 인터페이스 |
| **Backend** | FastAPI | REST API (선택사항) |
| **AI** | LangGraph, OpenAI | 에이전트 및 LLM |
| **Tools** | yfinance, numexpr | 주가 조회, 계산 |
| **Testing** | pytest | 비동기 테스트 |

## ⚠️ 주의사항

- **Yahoo Finance API**: 현재 429 에러 (Too Many Requests) 발생 가능
- **OpenAI API 키**: 반드시 `.env` 파일에 설정 필요  
- **네트워크**: 실시간 주가 조회를 위한 인터넷 연결 필요
- **가상환경**: `(stock-chatbot)` 환경에서 실행 권장

## 🧪 테스트

### pytest 테스트 실행 (권장)
```bash
# 모든 테스트 실행
pytest test/test_stock_agent.py -v

# 특정 테스트만 실행
pytest test/test_stock_agent.py::test_multi_turn_conversation -v

# 테스트 출력 보기
pytest test/test_stock_agent.py -v -s
```

### 직접 테스트
```bash
# AI 에이전트 직접 테스트
python test/test_stock_agent.py

# 간단한 스트리밍 테스트
python -c "
import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path.cwd()))

from ai.agent.stock_agent import StockAgent

async def test():
    agent = StockAgent()
    async for token in agent.stream_response('AAPL 주가 알려줘', 'test'):
        print(token, end='', flush=True)
    print()

asyncio.run(test())
"
```

### 테스트 시나리오
- **기본 주가 조회**: AAPL, TSLA 등 개별 주식 조회
- **계산 기능**: 수학 계산식 처리
- **Multi-turn 대화**: 이전 대화 기억하며 연속 질문
- **스트리밍 응답**: 토큰 단위 실시간 응답
- **복합 질문**: 주가 조회 + 계산 조합