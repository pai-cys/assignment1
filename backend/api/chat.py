"""채팅 관련 API 라우터"""
import uuid
import json
import logging
import sys
from pathlib import Path
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from ai.agent.stock_agent import StockAgent
from backend.dependencies import get_agent  # 1. 의존성 주입 함수를 가져옵니다.

router = APIRouter()
logger = logging.getLogger(__name__)

# 2. 전역 변수로 agent를 직접 생성하는 코드를 삭제합니다.
# agent = StockAgent() <-- 이 줄이 삭제되었습니다.

class ChatRequest(BaseModel):
    message: str
    thread_id: str = None

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    agent: StockAgent = Depends(get_agent)  # 3. Depends를 사용해 agent를 주입받습니다.
):
    """스트리밍 채팅 - LangGraph 기반"""
    try:
        thread_id = request.thread_id or str(uuid.uuid4())
        
        async def generate():
            try:
                # 주입받은 agent 인스턴스를 사용합니다.
                async for chunk in agent.stream_response(request.message, thread_id):
                    yield f"data: {json.dumps({'chunk': chunk, 'thread_id': thread_id}, ensure_ascii=False)}\n\n"
                yield f"data: {json.dumps({'done': True, 'thread_id': thread_id}, ensure_ascii=False)}\n\n"
            except Exception as e:
                logger.error(f"Stream error: {e}")
                yield f"data: {json.dumps({'error': str(e), 'thread_id': thread_id}, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )
    except Exception as e:
        logger.error(f"Chat stream error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class ClearRequest(BaseModel):
    thread_id: str

@router.post("/clear")
async def clear_history(
    request: ClearRequest,
    agent: StockAgent = Depends(get_agent)  # 4. 여기에도 동일하게 주입받습니다.
):
    """대화 히스토리 초기화"""
    try:
        # 주입받은 agent 인스턴스를 사용합니다.
        agent.clear_history(request.thread_id)
        return {"message": f"Thread {request.thread_id} cleared"}
    except Exception as e:
        logger.error(f"Clear error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

