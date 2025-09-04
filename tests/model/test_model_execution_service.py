"""Model execution service 단위테스트."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_openai import ChatOpenAI
from src.model.model_execution_service import ModelExecutionService
from src.model.service import ModelService


class TestModelExecutionService:
    """ModelExecutionService 테스트"""
    
    @pytest.fixture
    def mock_model_service(self):
        """Mock ModelService 생성"""
        return AsyncMock(spec=ModelService)
    
    @pytest.fixture
    def model_execution_service(self, mock_model_service):
        """ModelExecutionService 인스턴스 생성"""
        return ModelExecutionService(mock_model_service)
    
    @pytest.mark.asyncio
    async def test_load_llm_model_success(self, model_execution_service, mock_model_service):
        """LLM 모델 로딩 성공 테스트"""
        # Mock 설정
        mock_model = MagicMock()
        mock_model.model_type = "llm"
        mock_model.model_config = {"model": "gpt-4o", "enable_tool_calling": True}
        mock_model.model_provider_id = 1
        
        mock_provider = MagicMock()
        mock_provider.model_vendor = "OpenAI"
        
        mock_model_service.get_model.return_value = mock_model
        mock_model_service.get_provider.return_value = mock_provider
        
        # 테스트 실행
        with patch('src.model.model_execution_service.ChatOpenAI') as mock_chat_openai:
            mock_llm = MagicMock()
            mock_chat_openai.return_value = mock_llm
            
            result = await model_execution_service.load_llm_model(1)
            
            # 검증
            assert result == mock_llm
            mock_chat_openai.assert_called_once()
            mock_model_service.get_model.assert_called_once_with(1)
            mock_model_service.get_provider.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_load_llm_model_not_found(self, model_execution_service, mock_model_service):
        """존재하지 않는 모델 로딩 테스트"""
        # Mock 설정
        mock_model_service.get_model.return_value = None
        
        # 테스트 실행 및 예외 검증
        with pytest.raises(ValueError, match="Model not found: model_id=1"):
            await model_execution_service.load_llm_model(1)
    
    @pytest.mark.asyncio
    async def test_load_llm_model_wrong_type(self, model_execution_service, mock_model_service):
        """잘못된 타입의 모델 로딩 테스트"""
        # Mock 설정
        mock_model = MagicMock()
        mock_model.model_type = "embedding"  # LLM이 아닌 타입
        
        mock_model_service.get_model.return_value = mock_model
        
        # 테스트 실행 및 예외 검증
        with pytest.raises(ValueError, match="model_id=1 is not a llm model"):
            await model_execution_service.load_llm_model(1)
    
    @pytest.mark.asyncio
    async def test_load_llm_model_provider_not_found(self, model_execution_service, mock_model_service):
        """프로바이더를 찾을 수 없는 경우 테스트"""
        # Mock 설정
        mock_model = MagicMock()
        mock_model.model_type = "llm"
        mock_model.model_provider_id = 1
        
        mock_model_service.get_model.return_value = mock_model
        mock_model_service.get_provider.return_value = None
        
        # 테스트 실행 및 예외 검증
        with pytest.raises(ValueError, match="Provider not found: provider_id=1"):
            await model_execution_service.load_llm_model(1)
    
    @pytest.mark.asyncio
    async def test_load_llm_model_unsupported_vendor(self, model_execution_service, mock_model_service):
        """지원하지 않는 벤더 테스트"""
        # Mock 설정
        mock_model = MagicMock()
        mock_model.model_type = "llm"
        mock_model.model_provider_id = 1
        
        mock_provider = MagicMock()
        mock_provider.model_vendor = "UnsupportedVendor"
        
        mock_model_service.get_model.return_value = mock_model
        mock_model_service.get_provider.return_value = mock_provider
        
        # 테스트 실행 및 예외 검증
        with pytest.raises(ValueError, match="지원하지 않는 벤더: UnsupportedVendor"):
            await model_execution_service.load_llm_model(1)
    
    @pytest.mark.asyncio
    async def test_get_model_info(self, model_execution_service, mock_model_service):
        """모델 정보 조회 테스트"""
        # Mock 설정
        expected_info = {
            "model_id": 1,
            "model_name": "gpt-4o",
            "model_type": "llm",
            "model_config": {"model": "gpt-4o"},
            "use_custom": False
        }
        mock_model_service.get_model_info.return_value = expected_info
        
        # 테스트 실행
        result = await model_execution_service.get_model_info(1)
        
        # 검증
        assert result == expected_info
        mock_model_service.get_model_info.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_get_available_models(self, model_execution_service, mock_model_service):
        """사용 가능한 모델 목록 조회 테스트"""
        # Mock 설정
        expected_models = [
            {
                "model_id": 1,
                "model_name": "gpt-4o",
                "model_type": "llm",
                "model_config": {"model": "gpt-4o"},
                "use_custom": False
            }
        ]
        mock_model_service.get_available_models.return_value = expected_models
        
        # 테스트 실행
        result = await model_execution_service.get_available_models("llm")
        
        # 검증
        assert result == expected_models
        mock_model_service.get_available_models.assert_called_once_with("llm")
