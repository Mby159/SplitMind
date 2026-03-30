import pytest
from splitmind.core.engine import SplitMindEngine, ExecutionConfig, ExecutionMode
from splitmind.providers.base import BaseProvider, ProviderInfo, ProviderCapability
from splitmind.providers import register_provider


class FailingProvider(BaseProvider):
    """Provider that always fails"""
    
    def _default_model(self) -> str:
        return "failing-model"
    
    def get_info(self):
        return ProviderInfo(
            name="failing",
            description="Provider that always fails",
            models=["failing-model"],
            capabilities=[ProviderCapability.CHAT],
            max_tokens=4096,
            supports_streaming=False
        )
    
    def generate(self, prompt, **kwargs):
        raise Exception("Failing provider always fails")
    
    async def generate_async(self, prompt, **kwargs):
        raise Exception("Failing provider always fails")


class WorkingProvider(BaseProvider):
    """Provider that always works"""
    
    def _default_model(self) -> str:
        return "working-model"
    
    def get_info(self):
        return ProviderInfo(
            name="working",
            description="Provider that always works",
            models=["working-model"],
            capabilities=[ProviderCapability.CHAT],
            max_tokens=4096,
            supports_streaming=False
        )
    
    def generate(self, prompt, **kwargs):
        return f"Working provider response: {prompt}"
    
    async def generate_async(self, prompt, **kwargs):
        return f"Working provider response: {prompt}"


# Register test providers
register_provider(FailingProvider)
register_provider(WorkingProvider)


class TestProviderFallback:
    """Test provider failure fallback behavior"""
    
    def test_fallback_from_failing_provider(self):
        """Test that system can fallback when a provider fails"""
        # Create engine with hybrid mode
        engine = SplitMindEngine(
            config=ExecutionConfig(
                execution_mode=ExecutionMode.HYBRID
            )
        )
        
        # Try to execute a task
        task = "Hello, what's 1+1?"
        result = engine.execute_sync(task)
        
        # Should succeed despite potentially failing providers
        assert result.success
        assert len(result.final_result) > 0
    
    def test_local_only_fallback(self):
        """Test fallback behavior in local only mode"""
        # Create engine with local only mode
        engine = SplitMindEngine(
            config=ExecutionConfig(
                execution_mode=ExecutionMode.LOCAL_ONLY
            )
        )
        
        # Try to execute a task
        task = "Hello, what's 1+1?"
        result = engine.execute_sync(task)
        
        # Should succeed with local processing
        assert result.success
        assert len(result.final_result) > 0
    
    def test_online_mode_fallback(self):
        """Test fallback behavior in online mode"""
        # Create engine with online mode
        engine = SplitMindEngine(
            config=ExecutionConfig(
                execution_mode=ExecutionMode.ONLINE
            )
        )
        
        # Try to execute a task
        task = "Hello, what's 1+1?"
        result = engine.execute_sync(task)
        
        # Should succeed with available providers
        assert result.success
        assert len(result.final_result) > 0
