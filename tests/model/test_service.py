"""Model service 단위테스트."""

import pytest
from unittest.mock import AsyncMock
from src.model.service import ModelService


class TestModelService:
    """ModelService 테스트"""
    
    @pytest.fixture
    def model_service(self):
        """ModelService 인스턴스 생성"""
        return ModelService()
    
    @pytest.mark.asyncio
    async def test_get_model_success(self, model_service):
        """모델 조회 성공 테스트"""
        model = await model_service.get_model(1)
        
        assert model is not None
        assert model.model_id == 1
        assert model.model_name == "gpt-4o"
        assert model.model_type == "llm"
        assert model.model_provider_id == 1
    
    @pytest.mark.asyncio
    async def test_get_model_not_found(self, model_service):
        """존재하지 않는 모델 조회 테스트"""
        model = await model_service.get_model(999)
        
        assert model is None
    
    @pytest.mark.asyncio
    async def test_get_models_by_type_llm(self, model_service):
        """LLM 타입 모델 조회 테스트"""
        models = await model_service.get_models_by_type("llm")
        
        assert isinstance(models, list)
        assert len(models) == 1
        assert models[0].model_type == "llm"
        assert models[0].model_name == "gpt-4o"
    
    @pytest.mark.asyncio
    async def test_get_models_by_type_embedding(self, model_service):
        """임베딩 타입 모델 조회 테스트 (현재는 지원하지 않음)"""
        models = await model_service.get_models_by_type("embedding")
        
        assert isinstance(models, list)
        assert len(models) == 0
    
    @pytest.mark.asyncio
    async def test_get_all_models(self, model_service):
        """모든 모델 조회 테스트"""
        models = await model_service.get_all_models()
        
        assert isinstance(models, list)
        assert len(models) == 1
        assert models[0].model_name == "gpt-4o"
    
    @pytest.mark.asyncio
    async def test_get_provider_success(self, model_service):
        """프로바이더 조회 성공 테스트"""
        provider = await model_service.get_provider(1)
        
        assert provider is not None
        assert provider.model_provider_id == 1
        assert provider.model_provider_name == "OpenAI"
        assert provider.model_vendor == "OpenAI"
    
    @pytest.mark.asyncio
    async def test_get_provider_not_found(self, model_service):
        """존재하지 않는 프로바이더 조회 테스트"""
        provider = await model_service.get_provider(999)
        
        assert provider is None
    
    @pytest.mark.asyncio
    async def test_get_all_providers(self, model_service):
        """모든 프로바이더 조회 테스트"""
        providers = await model_service.get_all_providers()
        
        assert isinstance(providers, list)
        assert len(providers) == 1
        assert providers[0].model_provider_name == "OpenAI"
    
    @pytest.mark.asyncio
    async def test_get_model_info_success(self, model_service):
        """모델 정보 조회 성공 테스트"""
        model_info = await model_service.get_model_info(1)
        
        assert model_info is not None
        assert model_info["model_id"] == 1
        assert model_info["model_name"] == "gpt-4o"
        assert model_info["model_type"] == "llm"
        assert model_info["use_custom"] is False
    
    @pytest.mark.asyncio
    async def test_get_model_info_not_found(self, model_service):
        """존재하지 않는 모델 정보 조회 테스트"""
        model_info = await model_service.get_model_info(999)
        
        assert model_info is None
    
    @pytest.mark.asyncio
    async def test_get_available_models_all(self, model_service):
        """사용 가능한 모든 모델 조회 테스트"""
        models = await model_service.get_available_models()
        
        assert isinstance(models, list)
        assert len(models) == 1
        assert models[0]["model_name"] == "gpt-4o"
    
    @pytest.mark.asyncio
    async def test_get_available_models_by_type(self, model_service):
        """타입별 사용 가능한 모델 조회 테스트"""
        models = await model_service.get_available_models("llm")
        
        assert isinstance(models, list)
        assert len(models) == 1
        assert models[0]["model_type"] == "llm"
