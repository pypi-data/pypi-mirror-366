"""
Configuration management for ContextCol SDK
"""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator
from .exceptions import ConfigError

# Load environment variables from .env file
load_dotenv()


class Config(BaseModel):
    """Configuration class for ContextCol SDK"""

    # Binance API Configuration
    binance_api_key: Optional[str] = Field(
        default=os.getenv("BINANCE_API_KEY"), description="Binance API Key"
    )
    binance_api_secret: Optional[str] = Field(
        default=os.getenv("BINANCE_API_SECRET"), description="Binance API Secret"
    )
    binance_testnet: bool = Field(
        default=os.getenv("BINANCE_TESTNET", "true").lower() == "true",
        description="Use Binance testnet",
    )

    # ContextCol API Configuration
    contextcol_api_key: Optional[str] = Field(
        default=os.getenv("CONTEXTCOL_API_KEY"), description="ContextCol API Key"
    )
    contextcol_base_url: str = Field(
        default=os.getenv("CONTEXTCOL_BASE_URL", "https://api.contextcol.com"),
        description="ContextCol API base URL",
    )
    contextcol_binance_proxy_service_api_key: str = Field(
        default=os.getenv("CONTEXTCOL_BINANCE_PROXY_SERVICE_API_KEY", ""),
        description="ContextCol Binance Proxy Service API Key",
    )
    contextcol_binance_proxy_service_base_url: str = Field(
        default=os.getenv(
            "CONTEXTCOL_BINANCE_PROXY_SERVICE_BASE_URL",
            "https://binance-proxy-service.contextcol.com",
        ),
        description="ContextCol Binance Proxy Service base URL",
    )
    contextcol_binance_credential_id: str = Field(
        default=os.getenv("CONTEXTCOL_BINANCE_CREDENTIAL_ID", ""),
        description="ContextCol Binance Credential ID",
    )
    binance_base_url: str = Field(
        default=os.getenv("BINANCE_BASE_URL", "https://api.binance.com"),
        description="Binance API base URL",
    )

    # General Configuration
    timeout: int = Field(
        default=int(os.getenv("TIMEOUT", "30")),
        description="Request timeout in seconds",
    )
    max_retries: int = Field(
        default=int(os.getenv("MAX_RETRIES", "3")),
        description="Maximum number of retries for failed requests",
    )

    trading_bot_id: Optional[str] = Field(
        default=os.getenv("TRADING_BOT_ID"), description="Trading Bot ID"
    )
    test_mode: bool = Field(
        default=os.getenv("TEST_MODE", "true").lower() == "true",
        description="Test mode",
    )
    contextcol_env: str = Field(
        default=os.getenv("CONTEXTCOL_ENV", "production"),
        description="ContextCol environment",
    )

    class Config:
        """Pydantic configuration"""

        env_prefix = ""
        case_sensitive = False

    @validator("binance_api_key")
    def validate_binance_api_key(cls, v):
        if v and len(v) < 10:
            raise ConfigError("Binance API key appears to be invalid")
        return v

    @validator("binance_api_secret")
    def validate_binance_api_secret(cls, v):
        if v and len(v) < 10:
            raise ConfigError("Binance API secret appears to be invalid")
        return v

    @validator("contextcol_api_key")
    def validate_contextcol_api_key(cls, v):
        if v and len(v) < 10:
            raise ConfigError("ContextCol API key appears to be invalid")
        return v

    @validator("timeout")
    def validate_timeout(cls, v):
        if v <= 0:
            raise ConfigError("Timeout must be positive")
        return v

    @validator("max_retries")
    def validate_max_retries(cls, v):
        if v < 0:
            raise ConfigError("Max retries must be non-negative")
        return v

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables"""
        return cls(
            binance_api_key=os.getenv("BINANCE_API_KEY"),
            binance_api_secret=os.getenv("BINANCE_API_SECRET"),
            binance_testnet=os.getenv("BINANCE_TESTNET", "true").lower() == "true",
            contextcol_api_key=os.getenv("CONTEXTCOL_API_KEY"),
            contextcol_base_url=os.getenv(
                "CONTEXTCOL_BASE_URL", "https://api.contextcol.com"
            ),
            contextcol_binance_proxy_service_api_key=os.getenv(
                "CONTEXTCOL_BINANCE_PROXY_SERVICE_API_KEY", ""
            ),
            contextcol_binance_proxy_service_base_url=os.getenv(
                "CONTEXTCOL_BINANCE_PROXY_SERVICE_BASE_URL",
                "https://binance-proxy-service.contextcol.com",
            ),
            contextcol_binance_credential_id=os.getenv(
                "CONTEXTCOL_BINANCE_CREDENTIAL_ID", ""
            ),
            timeout=int(os.getenv("TIMEOUT", "30")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            trading_bot_id=os.getenv("TRADING_BOT_ID"),
            binance_base_url=os.getenv("BINANCE_BASE_URL", "https://api.binance.com"),
            test_mode=os.getenv("TEST_MODE", "true").lower() == "true",
            contextcol_env=os.getenv("CONTEXTCOL_ENV", "production"),
        )

    def validate_required_for_contextcol(self):
        """Validate required configuration for ContextCol operations"""
        if not self.contextcol_api_key:
            raise ConfigError("ContextCol API key is required")
