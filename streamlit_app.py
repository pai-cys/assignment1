"""Streamlit 앱 - UI Layer"""
import os
import sys
import asyncio
import time
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from dotenv import load_dotenv

from src.chatbot.service import ChatbotService
from src.chatbot.entities import ChatbotConfig

# 환경변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="주가 계산 챗봇 v2.0",
    page_icon="💰",
    layout="centered"
)


@st.cache_resource
def init_chatbot():
    """챗봇 서비스 초기화 (의존성 주입)"""
    try:
        from src.chatbot.container import chatbot_container
        return chatbot_container.service()
    except Exception as e:
        st.error(f"챗봇 초기화 실패: {e}")
        return None


def check_environment():
    """환경 설정 체크"""
    if not os.getenv("OPENAI_API_KEY"):
        st.error("❌ OpenAI API 키가 설정되지 않았습니다!")
        st.info("📝 .env 파일에 OPENAI_API_KEY=your_api_key_here를 추가해주세요")
        st.stop()


def main():
    """메인 애플리케이션"""
    # 환경 체크
    check_environment()
    
    # 제목
    st.title("💰 주가 계산 챗봇 v2.0")
    st.caption("🏗️ Layered Architecture + uv + LangGraph")
    
    # 세션 상태 초기화
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'session_id' not in st.session_state:
        st.session_state.session_id = f"streamlit_{int(time.time())}"
    
    # 챗봇 서비스 로드
    chatbot_service = init_chatbot()
    if chatbot_service is None:
        st.stop()
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 아키텍처 정보
        with st.expander("🏗️ 아키텍처 정보"):
            st.markdown("""
            **새로운 Layered Architecture:**
            - `src/chatbot/` - 비즈니스 로직
            - `src/llm/` - LLM 추상화
            - `src/tools/` - 도구 서비스
            - `src/model/executors/` - 실행기
            - `webapp/` - Presentation Layer
            """)
        
        # 세션 초기화
        if st.button("🗑️ 대화 초기화"):
            try:
                chatbot_service.clear_session(st.session_state.session_id)
                st.session_state.messages = []
                st.success("대화가 초기화되었습니다!")
                st.rerun()
            except Exception as e:
                st.error(f"초기화 실패: {e}")
        
        st.divider()
        st.caption(f"Session: {st.session_state.session_id}")
    
    # 대화 기록 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # 사용자 입력 처리
    if prompt := st.chat_input("메시지를 입력하세요... (예: AAPL 주가 알려줘)"):
        # 사용자 메시지 추가 및 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # AI 응답 생성 및 스트리밍 표시
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            
            try:
                async def get_streaming_response():
                    full_response = ""
                    streaming_response = await chatbot_service.stream_chat(
                        st.session_state.session_id, 
                        prompt
                    )
                    
                    async for chunk in streaming_response.generator:
                        # 백엔드에서 받은 청크를 문자별로 타이핑 효과 적용
                        for char in chunk:
                            full_response += char
                            response_placeholder.write(full_response + "▋")  # 커서 효과
                            await asyncio.sleep(0.03)  # 타이핑 속도 조절
                        
                        # 청크 완료 후 커서 제거
                        response_placeholder.write(full_response)
                    
                    return full_response
                
                # 비동기 실행
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                final_response = loop.run_until_complete(get_streaming_response())
                loop.close()
                
                if final_response:
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": final_response
                    })
                else:
                    st.error("❌ 응답을 받을 수 없습니다.")
                    
            except Exception as e:
                st.error(f"❌ 오류: {e}")
    
    # 하단 정보
    with st.expander("ℹ️ 사용법 및 예시"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **주가 조회:**
            - "AAPL 주가 알려줘"
            - "테슬라 주식 가격은?"
            - "NVDA 현재가 확인해줘"
            """)
        
        with col2:
            st.markdown("""
            **계산:**
            - "100 * 1.5는?"
            - "sqrt(16) 계산해줘"
            - "2 + 3 * 4"
            """)
        
        st.markdown("""
        **복합 질문:**
        - "엔비디아 5주랑 아마존 8주를 두명이 돈을 모아 사려고 하는데, 각자 얼마나 돈 챙겨야 해?"
        """)


if __name__ == "__main__":
    main()
