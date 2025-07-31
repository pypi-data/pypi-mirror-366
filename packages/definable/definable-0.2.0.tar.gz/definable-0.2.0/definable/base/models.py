from pydantic import BaseModel
from typing import Any, Dict, Optional, List

class AgentInput(BaseModel):
    """Optional base class for agent inputs - you can use any type"""
    pass

class AgentOutput(BaseModel):
    """Optional base class for agent outputs - you can use any type"""
    pass

class AgentInfo(BaseModel):
    """Information about the agent"""
    name: str
    description: str
    version: str
    input_schema: Optional[Dict[str, Any]] = None  # Made optional
    output_schema: Optional[Dict[str, Any]] = None  # Made optional

class BuildConfig(BaseModel):
    """Build configuration from YAML"""
    python_version: str = "3.11"
    dependencies: List[str] = []
    system_packages: List[str] = []
    environment_variables: List[str] = []

class PlatformConfig(BaseModel):
    """Platform configuration"""
    name: str
    description: str
    version: str

class ConcurrencyConfig(BaseModel):
    """Concurrency settings"""
    max_concurrent_requests: int = 50
    request_timeout: int = 300

class AgentConfig(BaseModel):
    """Complete agent configuration"""
    build: BuildConfig
    agent: str  # "main.py:DemoAgent"
    platform: PlatformConfig
    concurrency: ConcurrencyConfig


class UserConfig(BaseModel):
    """User configuration stored in ~/.definable/config.yaml"""
    api_key: Optional[str] = None
    default_endpoint: Optional[str] = None
    default_name: Optional[str] = None
    editor: Optional[str] = None
    
    class Config:
        # Allow extra fields for future extensibility
        extra = "allow"