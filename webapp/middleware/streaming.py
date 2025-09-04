"""Streaming middleware for real-time response handling."""

import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

class StreamingMiddleware(BaseHTTPMiddleware):
    """
    StreamingMiddleware는 스트리밍 응답을 처리하기 위한 미들웨어입니다.

    스트리밍 응답은 서버에서 클라이언트로 데이터를 실시간 스트리밍 방식으로 전송하며, 이 미들웨어는 FastAPI 응답 흐름을 제어하여
    서버가 응답을 즉시 플러시(Flush)하고 클라이언트로 전송할 수 있도록 보장합니다.

    이 미들웨어가 없을 경우, 서버는 응답을 버퍼에 계속 쌓아두고 전체 응답이 끝날 때 한 번에 반환하는 현상이 발생할 수 있습니다.
    이 미들웨어는 이러한 버퍼링 문제를 해결하여 클라이언트가 실시간으로 데이터를 수신할 수 있도록 도와줍니다.
    """

    async def dispatch(self, request: Request, call_next):
        """요청을 처리하고 스트리밍 응답을 최적화합니다."""
        response = await call_next(request)
        
        # 스트리밍 엔드포인트인지 확인
        if self._is_streaming_endpoint(request):
            response = self._configure_streaming_response(response)
            logger.info(f"스트리밍 응답 설정 완료: {request.url.path}")
        
        return response
    
    def _is_streaming_endpoint(self, request: Request) -> bool:
        """스트리밍 엔드포인트인지 확인합니다."""
        streaming_paths = ["/chat/stream", "/stream"]
        return any(path in str(request.url.path) for path in streaming_paths)
    
    def _configure_streaming_response(self, response: Response) -> Response:
        """스트리밍 응답에 필요한 헤더를 설정합니다."""
        # Server-Sent Events (SSE) 헤더 설정
        response.headers["Content-Type"] = "text/event-stream"
        response.headers["Cache-Control"] = "no-cache"
        response.headers["Connection"] = "keep-alive"
        response.headers["X-Accel-Buffering"] = "no"  # Nginx 버퍼링 비활성화
        
        # CORS 헤더 (스트리밍용)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Expose-Headers"] = "Content-Type, Cache-Control"
        
        return response
