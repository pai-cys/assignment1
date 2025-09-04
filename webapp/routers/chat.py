"""Chat endpoints for chatbot functionality."""

import logging
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse

from webapp.dependency import chatbot_service_dependency
from webapp.dtos import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="", tags=["Chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chatbot_service = Depends(chatbot_service_dependency)
):
    """일반 채팅"""
    try:
        session_id = request.session_id or f"session_{uuid4()}"
        response = await chatbot_service.chat(session_id, request.message)
        
        return ChatResponse(
            content=response.content,
            session_id=response.session_id,
            message_id=response.message_id,
            timestamp=response.timestamp
        )
        
    except Exception as e:
        logger.error(f"채팅 처리 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream")
async def stream_chat(
    request: ChatRequest,
    chatbot_service = Depends(chatbot_service_dependency)
):
    """스트리밍 채팅"""
    try:
        session_id = request.session_id or f"session_{uuid4()}"
        streaming_response = await chatbot_service.stream_chat(session_id, request.message)
        
        async def generate():
            try:
                async for chunk in streaming_response.generator:
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                logger.error(f"스트리밍 중 오류: {e}")
                yield f"data: ERROR: {str(e)}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",  # SSE 형식으로 변경
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Nginx 버퍼링 비활성화
                "X-Session-ID": session_id
            }
        )
        
    except Exception as e:
        logger.error(f"스트리밍 채팅 처리 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear/{session_id}")
async def clear_session(
    session_id: str,
    chatbot_service = Depends(chatbot_service_dependency)
):
    """세션 초기화"""
    try:
        chatbot_service.clear_session(session_id)
        return {"message": f"세션 {session_id}가 초기화되었습니다"}
    except Exception as e:
        logger.error(f"세션 초기화 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
