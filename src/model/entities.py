"""Model entities for database mapping."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

@dataclass
class ModelEntity:
    """모델 엔티티 (DB 매핑용)"""
    model_id: Optional[int]
    model_provider_id: int
    model_name: str
    model_type: str
    model_config: Dict
    use_custom: bool
    is_deleted: bool
    created_at: datetime
    
    @staticmethod
    def from_domain(domain: "Model") -> "ModelEntity":
        """도메인 모델에서 엔티티로 변환"""
        entity = ModelEntity(
            model_provider_id=domain.model_provider_id,
            model_name=domain.model_name,
            model_type=domain.model_type,
            model_config=domain.model_config,
            use_custom=domain.use_custom,
            is_deleted=domain.is_deleted,
            created_at=domain.created_at,
        )
        
        # model_id가 None이 아닌 경우에만 설정
        if domain.model_id is not None:
            entity.model_id = domain.model_id
            
        return entity

    def to_domain(self) -> "Model":
        """엔티티에서 도메인 모델로 변환"""
        from src.model.domains import Model
        return Model(
            model_id=self.model_id,
            model_provider_id=self.model_provider_id,
            model_name=self.model_name,
            model_type=self.model_type,
            model_config=self.model_config,
            use_custom=self.use_custom,
            is_deleted=self.is_deleted,
            created_at=self.created_at,
        )

    def primary_key(self) -> Optional[int]:
        """기본키 반환"""
        return self.model_id

@dataclass
class ModelProviderEntity:
    """모델 프로바이더 엔티티 (DB 매핑용)"""
    model_provider_id: Optional[int]
    model_provider_name: str
    model_key_id: Optional[int]
    model_vendor: str
    is_deleted: bool
    created_at: datetime
    
    @staticmethod
    def from_domain(domain: "ModelProvider") -> "ModelProviderEntity":
        """도메인 모델에서 엔티티로 변환"""
        entity = ModelProviderEntity(
            model_provider_name=domain.model_provider_name,
            model_key_id=domain.model_key_id,
            model_vendor=domain.model_vendor,
            is_deleted=domain.is_deleted,
            created_at=domain.created_at
        )
        
        # model_provider_id가 None이 아닌 경우에만 설정
        if domain.model_provider_id is not None:
            entity.model_provider_id = domain.model_provider_id
            
        return entity

    def to_domain(self) -> "ModelProvider":
        """엔티티에서 도메인 모델로 변환"""
        from src.model.domains import ModelProvider
        return ModelProvider(
            model_provider_id=self.model_provider_id,
            model_provider_name=self.model_provider_name,
            model_key_id=self.model_key_id,
            model_vendor=self.model_vendor,
            is_deleted=self.is_deleted,
            created_at=self.created_at
        )

    def primary_key(self) -> Optional[int]:
        """기본키 반환"""
        return self.model_provider_id

@dataclass
class ModelKeyEntity:
    """모델 키 엔티티 (DB 매핑용)"""
    model_key_id: Optional[int]
    key_name: str
    key_value: str
    
    @staticmethod
    def from_domain(domain: "ModelKey") -> "ModelKeyEntity":
        """도메인 모델에서 엔티티로 변환"""
        entity = ModelKeyEntity(
            key_name=domain.key_name,
            key_value=domain.key_value
        )
        
        # model_key_id가 None이 아닌 경우에만 설정
        if domain.model_key_id is not None:
            entity.model_key_id = domain.model_key_id
            
        return entity

    def to_domain(self) -> "ModelKey":
        """엔티티에서 도메인 모델로 변환"""
        from src.model.domains import ModelKey
        return ModelKey(
            model_key_id=self.model_key_id,
            key_name=self.key_name,
            key_value=self.key_value
        )

    def primary_key(self) -> Optional[int]:
        """기본키 반환"""
        return self.model_key_id
