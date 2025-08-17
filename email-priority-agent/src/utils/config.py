"""
Configuration management for the Email Priority Agent
"""

from typing import Optional, Dict, Any, List
import os
from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import Field, validator
import yaml


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Keys
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    twilio_account_sid: Optional[str] = Field(None, env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = Field(None, env="TWILIO_AUTH_TOKEN")
    
    # Database
    database_url: str = Field(
        "postgresql+asyncpg://user:password@localhost/email_priority",
        env="DATABASE_URL"
    )
    redis_url: str = Field("redis://localhost:6379", env="REDIS_URL")
    
    # Qdrant Vector Database
    qdrant_host: str = Field("localhost", env="QDRANT_HOST")
    qdrant_port: int = Field(6333, env="QDRANT_PORT")
    qdrant_api_key: Optional[str] = Field(None, env="QDRANT_API_KEY")
    
    # Email Configuration
    imap_server: str = Field("imap.gmail.com", env="IMAP_SERVER")
    imap_port: int = Field(993, env="IMAP_PORT")
    email_address: Optional[str] = Field(None, env="EMAIL_ADDRESS")
    email_password: Optional[str] = Field(None, env="EMAIL_PASSWORD")
    
    # Agent Configuration
    llm_provider: str = Field("openai", env="LLM_PROVIDER")  # "openai" or "anthropic"
    llm_model: str = Field("gpt-4-turbo-preview", env="LLM_MODEL")
    embedding_model: str = Field("text-embedding-3-small", env="EMBEDDING_MODEL")
    
    # Memory System
    working_memory_size: int = Field(20, env="WORKING_MEMORY_SIZE")
    short_term_memory_size: int = Field(100, env="SHORT_TERM_MEMORY_SIZE")
    memory_consolidation_interval: int = Field(300, env="MEMORY_CONSOLIDATION_INTERVAL")
    
    # Priority Thresholds
    critical_threshold: float = Field(0.9, env="CRITICAL_THRESHOLD")
    high_threshold: float = Field(0.75, env="HIGH_THRESHOLD")
    medium_threshold: float = Field(0.5, env="MEDIUM_THRESHOLD")
    low_threshold: float = Field(0.25, env="LOW_THRESHOLD")
    
    # Processing
    batch_size: int = Field(10, env="BATCH_SIZE")
    processing_interval: int = Field(60, env="PROCESSING_INTERVAL")  # seconds
    max_retries: int = Field(3, env="MAX_RETRIES")
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Features
    enable_sms: bool = Field(True, env="ENABLE_SMS")
    enable_email: bool = Field(True, env="ENABLE_EMAIL")
    enable_auto_learn: bool = Field(True, env="ENABLE_AUTO_LEARN")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator("llm_provider")
    def validate_llm_provider(cls, v):
        if v not in ["openai", "anthropic"]:
            raise ValueError("LLM provider must be 'openai' or 'anthropic'")
        return v
    
    @validator("openai_api_key")
    def validate_openai_key(cls, v, values):
        if values.get("llm_provider") == "openai" and not v:
            raise ValueError("OpenAI API key required when using OpenAI provider")
        return v
    
    @validator("anthropic_api_key")
    def validate_anthropic_key(cls, v, values):
        if values.get("llm_provider") == "anthropic" and not v:
            raise ValueError("Anthropic API key required when using Anthropic provider")
        return v


class ConfigManager:
    """Manages configuration from multiple sources"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("config/settings.yaml")
        self.settings = Settings()
        self._config_data = self._load_config_file()
        
    def _load_config_file(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def get_sender_rules(self) -> Dict[str, Any]:
        """Get sender-specific rules"""
        return self._config_data.get("sender_rules", {})
    
    def get_keyword_rules(self) -> Dict[str, Any]:
        """Get keyword-based rules"""
        return self._config_data.get("keyword_rules", {})
    
    def get_vip_list(self) -> List[str]:
        """Get list of VIP email addresses"""
        return self._config_data.get("vip_emails", [])
    
    def get_priority_overrides(self) -> Dict[str, float]:
        """Get manual priority overrides"""
        return self._config_data.get("priority_overrides", {})
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration and save to file"""
        self._config_data.update(updates)
        with open(self.config_path, 'w') as f:
            yaml.dump(self._config_data, f, default_flow_style=False)


# Global settings instance
_settings: Optional[Settings] = None
_config_manager: Optional[ConfigManager] = None


def get_settings() -> Settings:
    """Get the global settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def get_config_manager() -> ConfigManager:
    """Get the global config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager