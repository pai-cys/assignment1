"""
주가 계산 챗봇 - 최소한의 UI
"""
import streamlit as st
import asyncio
import time
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from ai.agent.stock_agent import StockAgent

# 페이지 설정
st.set_page_config(
    page_title="주가 계산 챗봇",
    page_icon="💰",
    layout="centered"
)

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'thread_id' not in st.session_state:
    st.session_state.thread_id = f"chat_{int(time.time())}"

# 에이전트 초기화
@st.cache_resource
def init_agent():
    try:
        return StockAgent()
    except Exception as e:
        st.error(f"AI 초기화 실패: {e}")
        return None

# 제목
st.title("💰 주가 계산 챗봇")

# 에이전트 로드
if st.session_state.agent is None:
    with st.spinner("🤖 AI 로딩중..."):
        st.session_state.agent = init_agent()

if st.session_state.agent is None:
    st.error("❌ OpenAI API 키를 확인해주세요.")
    st.stop()

# 대화 기록 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 입력 처리
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 추가 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # AI 응답 생성 및 실시간 스트리밍 표시
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        try:
            async def stream_response():
                full_response = ""
                async for token in st.session_state.agent.stream_response(
                    prompt, st.session_state.thread_id
                ):
                    full_response += token
                    # 실시간으로 응답 업데이트
                    response_placeholder.write(full_response)
                return full_response
            
            # 비동기 실행
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            final_response = loop.run_until_complete(stream_response())
            loop.close()
            
            if final_response:
                st.session_state.messages.append({"role": "assistant", "content": final_response})
            else:
                st.error("❌ 응답을 받을 수 없습니다.")
                
        except Exception as e:
            st.error(f"❌ 오류: {e}")

# 초기화 버튼 제거