"""Model domains 단위테스트."""

import pytest
from datetime import datetime
from src.model.domains import (
    Model, ModelProvider, ModelKey, ProviderModel,
    get_provider_models, get_provider_model, get_default_models, get_models_by_type
)


class TestModel:
    """Model 도메인 모델 테스트"""
    
    def test_model_new(self):
        """새 모델 생성 테스트"""
        model = Model.new(
            model_provider_id=1,
            model_name="gpt-4o",
            model_type="llm",
            model_config={"model": "gpt-4o", "enable_tool_calling": True},
            use_custom=False
        )
        
        assert model.model_id is None
        assert model.model_provider_id == 1
        assert model.model_name == "gpt-4o"
        assert model.model_type == "llm"
        assert model.model_config == {"model": "gpt-4o", "enable_tool_calling": True}
        assert model.use_custom is False
        assert model.is_deleted is False
        assert isinstance(model.created_at, datetime)
    
    def test_model_from_entity(self):
        """엔티티에서 도메인 모델로 변환 테스트"""
        class MockEntity:
            def __init__(self):
                self.model_id = 1
                self.model_provider_id = 1
                self.model_name = "gpt-4o"
                self.model_type = "llm"
                self.model_config = {"model": "gpt-4o"}
                self.use_custom = False
                self.is_deleted = False
                self.created_at = datetime.now()
        
        entity = MockEntity()
        model = Model.from_entity(entity)
        
        assert model.model_id == 1
        assert model.model_provider_id == 1
        assert model.model_name == "gpt-4o"
        assert model.model_type == "llm"
        assert model.model_config == {"model": "gpt-4o"}
        assert model.use_custom is False
        assert model.is_deleted is False


class TestModelProvider:
    """ModelProvider 도메인 모델 테스트"""
    
    def test_model_provider_new(self):
        """새 프로바이더 생성 테스트"""
        provider = ModelProvider.new(
            model_provider_name="OpenAI",
            model_vendor="OpenAI"
        )
        
        assert provider.model_provider_id is None
        assert provider.model_provider_name == "OpenAI"
        assert provider.model_vendor == "OpenAI"
        assert provider.model_key_id is None
        assert provider.is_deleted is False
        assert isinstance(provider.created_at, datetime)


class TestModelKey:
    """ModelKey 도메인 모델 테스트"""
    
    def test_model_key_creation(self):
        """모델 키 생성 테스트"""
        key = ModelKey(
            model_key_id=1,
            key_name="openai_api_key",
            key_value="sk-..."
        )
        
        assert key.model_key_id == 1
        assert key.key_name == "openai_api_key"
        assert key.key_value == "sk-..."


class TestProviderModel:
    """ProviderModel 테스트"""
    
    def test_provider_model_creation(self):
        """프로바이더 모델 생성 테스트"""
        provider_model = ProviderModel(
            name="gpt-4o",
            type="llm",
            config={"model": "gpt-4o", "enable_tool_calling": True},
            is_default=True
        )
        
        assert provider_model.name == "gpt-4o"
        assert provider_model.type == "llm"
        assert provider_model.config == {"model": "gpt-4o", "enable_tool_calling": True}
        assert provider_model.is_default is True


class TestProviderFunctions:
    """프로바이더 관련 함수 테스트"""
    
    def test_get_provider_models(self):
        """프로바이더 모델 목록 조회 테스트"""
        models = get_provider_models("OpenAI")
        
        assert isinstance(models, dict)
        assert "gpt-4o" in models
        assert models["gpt-4o"].name == "gpt-4o"
        assert models["gpt-4o"].type == "llm"
    
    def test_get_provider_models_invalid_vendor(self):
        """존재하지 않는 벤더 조회 테스트"""
        models = get_provider_models("InvalidVendor")
        
        assert models == {}
    
    def test_get_provider_model(self):
        """특정 프로바이더 모델 조회 테스트"""
        model = get_provider_model("OpenAI", "gpt-4o")
        
        assert model is not None
        assert model.name == "gpt-4o"
        assert model.type == "llm"
        assert model.is_default is True
    
    def test_get_provider_model_not_found(self):
        """존재하지 않는 모델 조회 테스트"""
        model = get_provider_model("OpenAI", "non-existent-model")
        
        assert model is None
    
    def test_get_default_models(self):
        """기본 모델 목록 조회 테스트"""
        default_models = get_default_models("OpenAI")
        
        assert isinstance(default_models, list)
        assert len(default_models) > 0
        assert all(model.is_default for model in default_models)
    
    def test_get_models_by_type(self):
        """타입별 모델 목록 조회 테스트"""
        llm_models = get_models_by_type("OpenAI", "llm")
        
        assert isinstance(llm_models, list)
        assert len(llm_models) > 0
        assert all(model.type == "llm" for model in llm_models)
