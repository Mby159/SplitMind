"""
SplitMind Engine - Main orchestration engine.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
import asyncio
from datetime import datetime

from splitmind.core.splitter import TaskSplitter, TaskSplitResult, SubTask, TaskType
from splitmind.core.aggregator import ResultAggregator, AggregatedResult, SubTaskResult, AggregationStrategy
from splitmind.core.privacy import PrivacyHandler
from splitmind.core.local_model import LocalModelInterface, LocalModelConfig, LocalModelBackend
from splitmind.providers.base import BaseProvider
from splitmind.providers.registry import ProviderRegistry


class ExecutionMode(str, Enum):
    """Execution mode for SplitMind Engine."""
    LOCAL_ONLY = "local_only"  # All processing done locally
    HYBRID = "hybrid"  # Privacy local, execution can use online providers
    ONLINE = "online"  # Can use online services for splitting and execution


class ExecutionConfig(BaseModel):
    max_concurrent_tasks: int = 5
    timeout_per_task: int = 60
    retry_failed_tasks: bool = True
    max_retries: int = 2
    enable_privacy_protection: bool = True
    default_strategy: AggregationStrategy = AggregationStrategy.PARALLEL_MERGE
    execution_mode: ExecutionMode = ExecutionMode.HYBRID  # User can choose execution mode


class ExecutionResult(BaseModel):
    success: bool
    final_result: str
    original_task: str
    split_result: Optional[TaskSplitResult] = None
    aggregated_result: Optional[AggregatedResult] = None
    privacy_report: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SplitMindEngine:
    """
    SplitMind Engine - Orchestrates the entire task execution pipeline.
    
    Supports three execution modes:
    - LOCAL_ONLY: All processing done locally (maximum privacy)
    - HYBRID: Privacy protection local, execution can use online providers (balanced)
    - ONLINE: Can use online services for splitting and execution (maximum capability)
    
    Pipeline:
    1. Privacy Analysis - Detect and redact sensitive information (always local)
    2. Task Splitting - Break down into independent subtasks
    3. Task Routing - Assign subtasks to AI providers
    4. Parallel Execution - Execute subtasks concurrently
    5. Result Aggregation - Combine results into final output
    6. Privacy Restoration - Restore sensitive information if needed
    """
    
    def __init__(
        self,
        providers: Optional[List[BaseProvider]] = None,
        config: Optional[ExecutionConfig] = None,
        privacy_handler: Optional[PrivacyHandler] = None,
        task_splitter: Optional[TaskSplitter] = None,
        result_aggregator: Optional[ResultAggregator] = None,
        local_model_config: Optional[LocalModelConfig] = None,
    ):
        self.config = config or ExecutionConfig()
        self.privacy_handler = privacy_handler or PrivacyHandler()
        self.task_splitter = task_splitter or TaskSplitter()
        self.result_aggregator = result_aggregator or ResultAggregator(
            default_strategy=self.config.default_strategy
        )
        self.local_model = LocalModelInterface(local_model_config) if local_model_config else None
        
        # Provider registry for online AI services
        self._registry = ProviderRegistry()
        if providers:
            for provider in providers:
                self._registry.register(provider)
    
    def register_provider(self, provider: BaseProvider) -> None:
        """Register an online AI provider."""
        self._registry.register(provider)
    
    def unregister_provider(self, name: str) -> bool:
        """Unregister an online AI provider."""
        return self._registry.unregister(name)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available online AI providers."""
        return self._registry.list_providers()
    
    async def execute(
        self,
        task: str,
        context: Optional[str] = None,
        split_strategy: str = "auto",
        providers: Optional[List[str]] = None,
    ) -> ExecutionResult:
        """
        Execute a task with privacy-preserving multi-agent orchestration.
        
        The execution mode is determined by self.config.execution_mode:
        - LOCAL_ONLY: All processing done locally
        - HYBRID: Privacy local, execution can use online providers
        - ONLINE: Can use online services for splitting and execution
        """
        start_time = datetime.now()
        
        try:
            full_input = f"{context}\n\n{task}" if context else task
            
            # Step 1: Privacy Analysis (always local)
            privacy_report = None
            if self.config.enable_privacy_protection:
                report = self.privacy_handler.generate_report(full_input)
                privacy_report = {
                    "total_detected": report.total_items_detected,
                    "items_by_type": report.items_by_type,
                    "risk_level": report.overall_risk_level.value,
                }
            
            # Step 2: Task Splitting
            if self.config.execution_mode == ExecutionMode.ONLINE and self._registry.list_providers():
                # Use online AI for task splitting if available
                split_result = await self._split_with_online(task, context, split_strategy)
            else:
                # Use local task splitting
                split_result = self.task_splitter.split(
                    task=task,
                    context=context,
                    strategy=split_strategy,
                )
            
            # Step 3 & 4: Task Routing and Execution
            if self.config.execution_mode == ExecutionMode.LOCAL_ONLY:
                # Use local model for execution
                subtask_results = await self._execute_with_local(split_result.subtasks)
            elif self.config.execution_mode == ExecutionMode.HYBRID:
                # Use online providers for execution (tasks are already redacted)
                if self._registry.list_providers():
                    subtask_results = await self._execute_with_online(split_result.subtasks, providers)
                else:
                    # Fallback to local if no providers available
                    subtask_results = await self._execute_with_local(split_result.subtasks)
            else:  # ONLINE mode
                if self._registry.list_providers():
                    subtask_results = await self._execute_with_online(split_result.subtasks, providers)
                else:
                    subtask_results = await self._execute_with_local(split_result.subtasks)
            
            # Step 5: Result Aggregation
            aggregated = self.result_aggregator.aggregate(
                results=subtask_results,
                strategy=self.config.default_strategy,
                context=task,
            )
            
            # Step 6: Privacy Restoration
            all_sensitive = {}
            for st in split_result.subtasks:
                all_sensitive.update(st.sensitive_info)
            
            if all_sensitive:
                aggregated.final_result = self.result_aggregator.restore_sensitive_info(
                    aggregated.final_result,
                    all_sensitive,
                )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            metadata = {
                "execution_mode": self.config.execution_mode.value,
                "local_model_used": bool(self.local_model and self.local_model.is_available()),
                "split_strategy_used": split_strategy,
                "providers_used": list(set(r.provider for r in subtask_results)),
            }
            
            return ExecutionResult(
                success=True,
                final_result=aggregated.final_result,
                original_task=task,
                split_result=split_result,
                aggregated_result=aggregated,
                privacy_report=privacy_report,
                execution_time=execution_time,
                metadata=metadata,
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ExecutionResult(
                success=False,
                final_result=f"Execution failed: {str(e)}",
                original_task=task,
                execution_time=execution_time,
                metadata={"error": str(e)},
            )
    
    async def _split_with_online(
        self,
        task: str,
        context: Optional[str],
        strategy: str,
    ) -> TaskSplitResult:
        """Use online AI for task splitting."""
        # For now, fall back to local splitting
        # TODO: Implement online splitting using LLM
        return self.task_splitter.split(task, context, strategy)
    
    async def _execute_with_local(
        self,
        subtasks: List[SubTask],
    ) -> List[SubTaskResult]:
        """Execute subtasks using local model."""
        subtask_results = []
        
        for subtask in subtasks:
            if self.local_model and self.local_model.is_available():
                try:
                    start = datetime.now()
                    result = self.local_model.generate(subtask.input_data)
                    execution_time = (datetime.now() - start).total_seconds()
                    
                    subtask_results.append(SubTaskResult(
                        subtask_id=subtask.id,
                        provider="local_model",
                        result=result,
                        success=True,
                        execution_time=execution_time,
                    ))
                except Exception as e:
                    subtask_results.append(SubTaskResult(
                        subtask_id=subtask.id,
                        provider="local_model",
                        result="",
                        success=False,
                        error=str(e),
                    ))
            else:
                # Fallback: use simple processing if no local model
                subtask_results.append(SubTaskResult(
                    subtask_id=subtask.id,
                    provider="local_processing",
                    result=f"Processed: {subtask.description}",
                    success=True,
                ))
        
        return subtask_results
    
    async def _execute_with_online(
        self,
        subtasks: List[SubTask],
        providers: Optional[List[str]] = None,
    ) -> List[SubTaskResult]:
        """Execute subtasks using online providers."""
        semaphore = asyncio.Semaphore(self.config.max_concurrent_tasks)
        
        async def execute_single(subtask: SubTask, provider_name: str) -> SubTaskResult:
            async with semaphore:
                provider = self._registry.get(provider_name)
                if not provider:
                    return SubTaskResult(
                        subtask_id=subtask.id,
                        provider=provider_name,
                        result="",
                        success=False,
                        error=f"Provider {provider_name} not found",
                    )
                
                retries = self.config.max_retries if self.config.retry_failed_tasks else 1
                
                for attempt in range(retries):
                    try:
                        start = datetime.now()
                        result = await provider.generate_async(
                            prompt=subtask.input_data,
                            task_type=subtask.task_type.value,
                        )
                        execution_time = (datetime.now() - start).total_seconds()
                        
                        return SubTaskResult(
                            subtask_id=subtask.id,
                            provider=provider_name,
                            result=result,
                            success=True,
                            execution_time=execution_time,
                        )
                    except Exception as e:
                        if attempt == retries - 1:
                            return SubTaskResult(
                                subtask_id=subtask.id,
                                provider=provider_name,
                                result="",
                                success=False,
                                error=str(e),
                            )
                        await asyncio.sleep(1)
                
                return SubTaskResult(
                    subtask_id=subtask.id,
                    provider=provider_name,
                    result="",
                    success=False,
                    error="Max retries exceeded",
                )
        
        # Route subtasks to providers
        available_providers = providers or self._registry.list_providers()
        if not available_providers:
            # Fallback to local if no providers
            return await self._execute_with_local(subtasks)
        
        tasks = []
        for idx, subtask in enumerate(subtasks):
            provider = available_providers[idx % len(available_providers)]
            tasks.append(execute_single(subtask, provider))
        
        return await asyncio.gather(*tasks)
    
    def execute_sync(
        self,
        task: str,
        context: Optional[str] = None,
        split_strategy: str = "auto",
        providers: Optional[List[str]] = None,
    ) -> ExecutionResult:
        """Synchronous version of execute."""
        return asyncio.run(self.execute(task, context, split_strategy, providers))
    
    def analyze_task(self, task: str) -> Dict[str, Any]:
        """Analyze a task and return structured information."""
        task_type = self.task_splitter.analyze_task_type(task)
        sensitive = self.task_splitter.detect_sensitive_info(task)
        privacy_report = self.privacy_handler.generate_report(task)
        
        analysis = {
            "task_type": task_type.value,
            "sensitive_info_detected": sensitive,
            "privacy_risk_level": privacy_report.overall_risk_level.value,
            "recommended_strategy": self._recommend_strategy(task_type, privacy_report),
            "execution_mode": self.config.execution_mode.value,
        }
        
        # Use local model for enhanced analysis if available
        if self.local_model and self.local_model.is_available():
            try:
                local_analysis = self.local_model.analyze_task(task)
                analysis.update({
                    "local_model_analysis": local_analysis,
                    "enhanced_task_type": local_analysis.get("task_type", task_type.value),
                    "enhanced_complexity": local_analysis.get("complexity", "medium"),
                })
            except Exception:
                pass
        
        return analysis
    
    def _recommend_strategy(
        self,
        task_type: TaskType,
        privacy_report: Any,
    ) -> str:
        """Recommend a splitting strategy based on task type and privacy risk."""
        if privacy_report.overall_risk_level.value in ["high", "critical"]:
            return "parallel"
        
        if task_type == TaskType.ANALYSIS:
            return "parallel"
        
        if task_type in [TaskType.SUMMARIZATION, TaskType.TRANSLATION]:
            return "single"
        
        return "auto"
    
    def preview_split(
        self,
        task: str,
        context: Optional[str] = None,
        strategy: str = "auto",
    ) -> Dict[str, Any]:
        """Preview how a task will be split without executing."""
        split_result = self.task_splitter.split(task, context, strategy)
        
        return {
            "original_task": split_result.original_task,
            "task_type": split_result.task_type.value,
            "split_strategy": split_result.split_strategy,
            "execution_mode": self.config.execution_mode.value,
            "subtasks": [
                {
                    "id": st.id,
                    "description": st.description,
                    "task_type": st.task_type.value,
                    "input_preview": st.input_data[:200] + "..." if len(st.input_data) > 200 else st.input_data,
                    "sensitive_info_count": len(st.sensitive_info),
                }
                for st in split_result.subtasks
            ],
            "total_subtasks": len(split_result.subtasks),
        }
