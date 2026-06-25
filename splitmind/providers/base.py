"""
Base Provider - Abstract base class for AI providers.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from enum import Enum


class ProviderCapability(str, Enum):
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"


class ProviderStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    UNKNOWN = "unknown"


class ProviderInfo(BaseModel):
    name: str
    description: str
    models: List[str]
    capabilities: List[ProviderCapability]
    max_tokens: int
    supports_streaming: bool = True


class GenerationConfig(BaseModel):
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: Optional[List[str]] = None


class BaseProvider(ABC):
    """
    Abstract base class for AI providers.

    All AI provider implementations must inherit from this class
    and implement the required methods.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        config: Optional[GenerationConfig] = None,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model or self._default_model()
        self.config = config or GenerationConfig()
        self._client = None

    @abstractmethod
    def _default_model(self) -> str:
        pass

    @abstractmethod
    def get_info(self) -> ProviderInfo:
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        task_type: Optional[str] = None,
        **kwargs,
    ) -> str:
        pass

    @abstractmethod
    async def generate_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        task_type: Optional[str] = None,
        **kwargs,
    ) -> str:
        pass

    def _build_system_prompt(self, task_type: Optional[str]) -> str:
        base_prompt = "You are a helpful AI assistant."

        task_prompts = {
            "analysis": "You are an analytical AI assistant. Provide thorough, structured analysis.",
            "generation": "You are a creative AI assistant. Generate high-quality content.",
            "summarization": "You are a summarization expert. Provide concise, accurate summaries.",
            "translation": "You are a professional translator. Provide accurate translations.",
            "extraction": "You are an information extraction expert. Extract key information accurately.",
            "classification": "You are a classification expert. Categorize information accurately.",
            "reasoning": "You are a logical reasoning expert. Provide clear, step-by-step reasoning.",
        }

        if task_type and task_type in task_prompts:
            return task_prompts[task_type]

        return base_prompt

    @staticmethod
    def build_placeholder_preservation_instruction(
        placeholders: Optional[List[str]],
    ) -> str:
        """Build a privacy instruction telling the model to preserve placeholders.

        Only placeholder IDs (e.g. ``[REDACTED_EMAIL_0]``) are passed here.
        The original sensitive values are never included; they stay local.
        Returns an empty string when there are no placeholders.
        """
        if not placeholders:
            return ""
        ids = ", ".join(sorted(set(placeholders)))
        return (
            "The user input contains privacy placeholders such as "
            f"{ids}. These are opaque tokens that replace redacted private "
            "information. Do not translate, alter, reformat, split, remove, or "
            "invent these placeholders. If you need to refer to a redacted value, "
            "copy the placeholder exactly as written. Do not ask for the original "
            "value."
        )

    def compose_system_prompt(
        self,
        task_type: Optional[str] = None,
        system_prompt: Optional[str] = None,
        placeholders: Optional[List[str]] = None,
    ) -> str:
        """Compose the task system prompt with optional placeholder rules.

        Uses ``system_prompt`` if given, otherwise the provider's task prompt,
        then appends the placeholder-preservation instruction when placeholders
        are present.
        """
        base = system_prompt or self._build_system_prompt(task_type)
        instruction = self.build_placeholder_preservation_instruction(placeholders)
        if instruction:
            return f"{base}\n\n{instruction}"
        return base

    def _merge_config(self, **kwargs) -> Dict[str, Any]:
        config = {
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "top_p": kwargs.get("top_p", self.config.top_p),
            "frequency_penalty": kwargs.get("frequency_penalty", self.config.frequency_penalty),
            "presence_penalty": kwargs.get("presence_penalty", self.config.presence_penalty),
        }

        if self.config.stop_sequences or kwargs.get("stop"):
            config["stop"] = kwargs.get("stop", self.config.stop_sequences)

        return config

    def validate_connection(self) -> bool:
        try:
            result = self.generate("Hello, this is a connection test.", max_tokens=10)
            return len(result) > 0
        except Exception:
            return False

    async def validate_connection_async(self) -> bool:
        try:
            result = await self.generate_async("Hello, this is a connection test.", max_tokens=10)
            return len(result) > 0
        except Exception:
            return False

    def estimate_tokens(self, text: str) -> int:
        char_count = len(text)

        chinese_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        non_chinese_chars = char_count - chinese_chars

        estimated = chinese_chars * 2 + non_chinese_chars // 4

        return max(estimated, 1)

    def __repr__(self) -> str:
        info = self.get_info()
        return f"<{self.__class__.__name__}: {info.name} ({self.model})>"
