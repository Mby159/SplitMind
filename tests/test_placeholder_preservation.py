"""Tests for placeholder-preservation prompt injection.

When a subtask carries privacy placeholders (e.g. [REDACTED_EMAIL_0]), the
online provider must receive a system prompt that instructs it to preserve the
placeholders exactly. The original sensitive values must never be sent.
"""

from splitmind.core.engine import SplitMindEngine, ExecutionConfig, ExecutionMode
from splitmind.providers.base import (
    BaseProvider,
    ProviderInfo,
    ProviderCapability,
)
from splitmind.providers import register_provider


class CapturingProvider(BaseProvider):
    """Provider that records the prompts it receives."""

    last_prompt = None
    last_system_prompt = None
    response_template = None

    def _default_model(self) -> str:
        return "capturing-model"

    def get_info(self):
        return ProviderInfo(
            name="capturing",
            description="Provider that captures prompts",
            models=["capturing-model"],
            capabilities=[ProviderCapability.CHAT],
            max_tokens=4096,
            supports_streaming=False,
        )

    def generate(self, prompt, system_prompt=None, task_type=None, **kwargs):
        CapturingProvider.last_prompt = prompt
        CapturingProvider.last_system_prompt = system_prompt
        if CapturingProvider.response_template is not None:
            return CapturingProvider.response_template.format(prompt=prompt)
        return f"echo: {prompt}"

    async def generate_async(self, prompt, system_prompt=None, task_type=None, **kwargs):
        CapturingProvider.last_prompt = prompt
        CapturingProvider.last_system_prompt = system_prompt
        if CapturingProvider.response_template is not None:
            return CapturingProvider.response_template.format(prompt=prompt)
        return f"echo: {prompt}"


register_provider(CapturingProvider)


class TestPlaceholderPreservationInstruction:
    """Unit tests for the base provider helper."""

    def test_empty_when_no_placeholders(self):
        assert BaseProvider.build_placeholder_preservation_instruction(None) == ""
        assert BaseProvider.build_placeholder_preservation_instruction([]) == ""

    def test_mentions_placeholders_and_rules(self):
        instr = BaseProvider.build_placeholder_preservation_instruction(
            ["[REDACTED_EMAIL_0]", "[REDACTED_PHONE_0]"]
        )
        assert "[REDACTED_EMAIL_0]" in instr
        assert "[REDACTED_PHONE_0]" in instr
        # Must instruct preservation, not modification.
        assert "Do not" in instr
        assert "copy the placeholder exactly" in instr

    def test_compose_appends_instruction_when_placeholders(self):
        provider = CapturingProvider()
        composed = provider.compose_system_prompt(
            task_type="analysis",
            placeholders=["[REDACTED_EMAIL_0]"],
        )
        assert "analytical AI assistant" in composed
        assert "[REDACTED_EMAIL_0]" in composed

    def test_compose_no_instruction_when_empty(self):
        provider = CapturingProvider()
        composed = provider.compose_system_prompt(
            task_type="analysis",
            placeholders=[],
        )
        assert "[REDACTED" not in composed


class TestEngineInjectsPreservationPrompt:
    """Integration test: engine routes placeholders into the system prompt."""

    def _run_online(self, task):
        engine = SplitMindEngine(
            providers=[CapturingProvider()],
            config=ExecutionConfig(execution_mode=ExecutionMode.ONLINE),
        )
        return engine.execute_sync(
            task, split_strategy="single", providers=["capturing"]
        )

    def test_system_prompt_contains_placeholders_and_no_raw_values(self):
        CapturingProvider.last_prompt = None
        CapturingProvider.last_system_prompt = None
        CapturingProvider.response_template = None

        task = "请分析这个客户需求，客户邮箱是 alice@example.com，手机号是 13800138000。"
        result = self._run_online(task)
        assert result.success

        system_prompt = CapturingProvider.last_system_prompt
        assert system_prompt is not None
        # Placeholder IDs must be present.
        assert "[REDACTED_EMAIL_0]" in system_prompt
        assert "[REDACTED_PHONE_0]" in system_prompt
        # Raw sensitive values must NOT leak into the system prompt.
        assert "alice@example.com" not in system_prompt
        assert "13800138000" not in system_prompt
        # The redacted prompt also must not contain raw values.
        assert "alice@example.com" not in CapturingProvider.last_prompt
        assert "13800138000" not in CapturingProvider.last_prompt

    def test_no_instruction_when_no_sensitive_info(self):
        CapturingProvider.last_prompt = None
        CapturingProvider.last_system_prompt = None
        CapturingProvider.response_template = None

        task = "Please summarize the benefits of unit testing."
        result = self._run_online(task)
        assert result.success

        system_prompt = CapturingProvider.last_system_prompt
        assert system_prompt is not None
        assert "[REDACTED" not in system_prompt


class TestPlaceholderValidationMetadata:
    """Engine records placeholder integrity evidence without fuzzy recovery."""

    def _run_online(self, task):
        engine = SplitMindEngine(
            providers=[CapturingProvider()],
            config=ExecutionConfig(execution_mode=ExecutionMode.ONLINE),
        )
        return engine.execute_sync(
            task, split_strategy="single", providers=["capturing"]
        )

    def setup_method(self):
        CapturingProvider.last_prompt = None
        CapturingProvider.last_system_prompt = None
        CapturingProvider.response_template = None

    def test_records_found_placeholders_before_restoration(self):
        CapturingProvider.response_template = "Provider kept placeholders: {prompt}"

        task = "请分析客户邮箱 alice@example.com 和手机号 13800138000。"
        result = self._run_online(task)

        validation = result.metadata["placeholder_validation"]
        assert validation["ok"] is True
        assert validation["expected_placeholders"] == [
            "[REDACTED_EMAIL_0]",
            "[REDACTED_PHONE_0]",
        ]
        assert validation["found_placeholders"] == validation["expected_placeholders"]
        assert validation["missing_placeholders"] == []
        assert validation["mangled_placeholders"] == []
        # Restoration still happens after validation.
        assert "alice@example.com" in result.final_result
        assert "13800138000" in result.final_result

    def test_records_missing_placeholders_without_recovery(self):
        CapturingProvider.response_template = "Provider omitted the private values."

        task = "请分析客户邮箱 alice@example.com 和手机号 13800138000。"
        result = self._run_online(task)

        validation = result.metadata["placeholder_validation"]
        assert validation["ok"] is False
        assert validation["expected_placeholders"] == [
            "[REDACTED_EMAIL_0]",
            "[REDACTED_PHONE_0]",
        ]
        assert validation["found_placeholders"] == []
        assert validation["missing_placeholders"] == validation["expected_placeholders"]
        assert validation["mangled_placeholders"] == []
        assert result.final_result == "Provider omitted the private values."

    def test_records_mangled_placeholders_without_fuzzy_recovery(self):
        CapturingProvider.response_template = (
            "Email token became REDACTED_EMAIL_0 but phone stayed [REDACTED_PHONE_0]."
        )

        task = "请分析客户邮箱 alice@example.com 和手机号 13800138000。"
        result = self._run_online(task)

        validation = result.metadata["placeholder_validation"]
        assert validation["ok"] is False
        assert validation["found_placeholders"] == ["[REDACTED_PHONE_0]"]
        assert validation["missing_placeholders"] == ["[REDACTED_EMAIL_0]"]
        assert validation["mangled_placeholders"] == ["REDACTED_EMAIL_0"]
        # Exact restoration only: the mangled email token is not guessed/recovered.
        assert "REDACTED_EMAIL_0" in result.final_result
        assert "alice@example.com" not in result.final_result
        assert "13800138000" in result.final_result
