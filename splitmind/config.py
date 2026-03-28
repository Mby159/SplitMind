"""
SplitMind Configuration Management
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel
from splitmind.core.engine import ExecutionMode

class SplitMindConfig(BaseModel):
    """SplitMind configuration model."""
    execution_mode: str = "hybrid"
    default_model: str = "llama3.2:3b"
    enable_privacy_protection: bool = True
    default_strategy: str = "auto"
    max_concurrent_tasks: int = 5
    timeout_per_task: int = 60
    retry_failed_tasks: bool = True
    max_retries: int = 2

class ConfigManager:
    """Configuration manager for SplitMind."""
    
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()
    
    def _get_config_dir(self) -> Path:
        """Get the configuration directory."""
        if Path.home():
            return Path.home() / ".splitmind"
        return Path(".") / ".splitmind"
    
    def _ensure_config_dir(self) -> None:
        """Ensure the configuration directory exists."""
        self.config_dir.mkdir(exist_ok=True)
    
    def load(self) -> SplitMindConfig:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return SplitMindConfig(**data)
            except (json.JSONDecodeError, ValueError):
                # If config file is invalid, return default
                return SplitMindConfig()
        return SplitMindConfig()
    
    def save(self, config: SplitMindConfig) -> None:
        """Save configuration to file."""
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config.model_dump(), f, indent=2, ensure_ascii=False)
    
    def get_execution_mode(self) -> ExecutionMode:
        """Get the default execution mode."""
        config = self.load()
        try:
            return ExecutionMode(config.execution_mode)
        except ValueError:
            return ExecutionMode.HYBRID
    
    def set_execution_mode(self, mode: ExecutionMode) -> None:
        """Set the default execution mode."""
        config = self.load()
        config.execution_mode = mode.value
        self.save(config)
    
    def get_default_model(self) -> str:
        """Get the default local model."""
        config = self.load()
        return config.default_model
    
    def set_default_model(self, model: str) -> None:
        """Set the default local model."""
        config = self.load()
        config.default_model = model
        self.save(config)
    
    def get_privacy_protection(self) -> bool:
        """Get privacy protection setting."""
        config = self.load()
        return config.enable_privacy_protection
    
    def set_privacy_protection(self, enabled: bool) -> None:
        """Set privacy protection setting."""
        config = self.load()
        config.enable_privacy_protection = enabled
        self.save(config)

# Global config manager instance
config_manager = ConfigManager()

# Environment settings
class Settings(BaseModel):
    """Environment settings."""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    kimi_api_key: Optional[str] = None
    local_model_url: str = "http://localhost:11434/api"
    local_model_name: str = "llama3.2:3b"

# Load settings from environment variables
import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

settings = Settings(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    kimi_api_key=os.getenv("KIMI_API_KEY"),
    local_model_url=os.getenv("LOCAL_MODEL_URL", "http://localhost:11434/api"),
    local_model_name=os.getenv("LOCAL_MODEL_NAME", "llama3.2:3b")
)
