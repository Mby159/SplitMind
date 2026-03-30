# SplitMind Plugin API Stability Guide

This document defines the stable API surface for SplitMind plugins, outlining which classes, methods, and fields are guaranteed to remain backward compatible.

## Core API Surface

### 1. BaseProvider Class

The `BaseProvider` abstract base class is the foundation for all provider implementations. The following methods and properties are guaranteed to remain stable:

#### Required Methods (Must be implemented by all providers):
- `_default_model() -> str`: Returns the default model name for the provider
- `get_info() -> ProviderInfo`: Returns provider information
- `generate(prompt: str, **kwargs) -> str`: Synchronous text generation
- `generate_async(prompt: str, **kwargs) -> str`: Asynchronous text generation

#### Optional Methods (Can be overridden):
- `validate_connection() -> bool`: Validates provider connection
- `validate_connection_async() -> bool`: Asynchronous connection validation
- `estimate_tokens(text: str) -> int`: Estimates token count for text

### 2. ProviderInfo Model

The `ProviderInfo` model defines the metadata for a provider. The following fields are stable:

- `name: str`: Provider name
- `description: str`: Provider description
- `models: List[str]`: List of supported models
- `capabilities: List[ProviderCapability]`: List of supported capabilities
- `max_tokens: int`: Maximum tokens for generation
- `supports_streaming: bool`: Whether streaming is supported

### 3. ProviderCapability Enum

The `ProviderCapability` enum defines the capabilities of a provider. The following values are stable:

- `CHAT`: Chat capability
- `COMPLETION`: Text completion capability
- `EMBEDDING`: Embedding capability
- `VISION`: Vision capability
- `FUNCTION_CALLING`: Function calling capability

### 4. ProviderStatus Enum

The `ProviderStatus` enum defines the status of a provider. The following values are stable:

- `ACTIVE`: Provider is active and ready
- `INACTIVE`: Provider is inactive
- `ERROR`: Provider has an error
- `UNKNOWN`: Provider status is unknown

### 5. Registry API

The provider registry API is stable and includes:

- `registry.list_providers() -> List[str]`: Lists available providers
- `registry.get(name: str) -> Optional[BaseProvider]`: Gets a provider instance
- `register_provider(provider_class: Type[BaseProvider]) -> None`: Registers a custom provider

## Execution API

### 1. ExecutionMode Enum

The `ExecutionMode` enum defines the execution mode for the engine. The following values are stable:

- `LOCAL_ONLY`: All processing done locally
- `HYBRID`: Privacy local, execution can use online providers
- `ONLINE`: Can use online services for splitting and execution

### 2. ExecutionConfig Model

The `ExecutionConfig` model defines the configuration for engine execution. The following fields are stable:

- `max_concurrent_tasks: int`: Maximum concurrent tasks
- `timeout_per_task: int`: Timeout per task in seconds
- `retry_failed_tasks: bool`: Whether to retry failed tasks
- `max_retries: int`: Maximum number of retries
- `enable_privacy_protection: bool`: Whether to enable privacy protection
- `default_strategy: AggregationStrategy`: Default aggregation strategy
- `execution_mode: ExecutionMode`: Execution mode

### 3. ExecutionResult Model

The `ExecutionResult` model defines the result of engine execution. The following fields are stable:

- `success: bool`: Whether execution succeeded
- `final_result: str`: The final result
- `original_task: str`: The original task
- `split_result: Optional[TaskSplitResult]`: The task split result
- `aggregated_result: Optional[AggregatedResult]`: The aggregated result
- `privacy_report: Optional[Dict[str, Any]]`: The privacy report
- `execution_time: float`: Execution time in seconds
- `metadata: Dict[str, Any]`: Additional metadata

## Privacy API

### 1. PrivacyHandler Class

The `PrivacyHandler` class provides privacy protection features. The following methods are stable:

- `detect(text: str) -> List[SensitiveInfo]`: Detects sensitive information
- `redact(text: str, strategy: str = "placeholder") -> Tuple[str, Dict[str, str]]`: Redacts sensitive information
- `restore(text: str, mapping: Dict[str, str]) -> str`: Restores redacted information
- `generate_report(text: str) -> PrivacyReport`: Generates a privacy report

### 2. SensitiveInfo Model

The `SensitiveInfo` model defines sensitive information. The following fields are stable:

- `info_type: str`: Type of sensitive information
- `original_value: str`: Original value
- `placeholder: str`: Placeholder value
- `position: Tuple[int, int]`: Position in text
- `confidence: float`: Confidence score
- `risk_level: RiskLevel`: Risk level
- `context: Optional[str]`: Context

### 3. RiskLevel Enum

The `RiskLevel` enum defines the risk level of sensitive information. The following values are stable:

- `LOW`: Low risk
- `MEDIUM`: Medium risk
- `HIGH`: High risk
- `CRITICAL`: Critical risk

## Task Splitting API

### 1. TaskSplitter Class

The `TaskSplitter` class splits tasks into subtasks. The following methods are stable:

- `split(task: str, context: Optional[str] = None, strategy: str = "auto") -> TaskSplitResult`: Splits a task
- `analyze_task_type(task: str) -> TaskType`: Analyzes task type

### 2. TaskType Enum

The `TaskType` enum defines the type of a task. The following values are stable:

- `ANALYSIS`: Analysis task
- `GENERATION`: Generation task
- `SUMMARIZATION`: Summarization task
- `TRANSLATION`: Translation task
- `EXTRACTION`: Extraction task
- `CLASSIFICATION`: Classification task
- `REASONING`: Reasoning task
- `MIXED`: Mixed task

### 3. SubTask Model

The `SubTask` model defines a subtask. The following fields are stable:

- `id: str`: Subtask ID
- `description: str`: Subtask description
- `task_type: TaskType`: Task type
- `input_data: str`: Input data
- `original_input: Optional[str]`: Original input
- `sensitive_info: Dict[str, str]`: Sensitive information
- `dependencies: List[str]`: Dependencies
- `status: SubTaskStatus`: Status
- `result: Optional[str]`: Result

## Result Aggregation API

### 1. ResultAggregator Class

The `ResultAggregator` class aggregates results from multiple providers. The following methods are stable:

- `aggregate(results: List[SubTaskResult], strategy: Optional[AggregationStrategy] = None, context: Optional[str] = None) -> AggregatedResult`: Aggregates results
- `detect_conflicts(results: List[SubTaskResult]) -> List[Dict[str, Any]]`: Detects conflicts

### 2. AggregationStrategy Enum

The `AggregationStrategy` enum defines the aggregation strategy. The following values are stable:

- `SEQUENTIAL`: Sequential aggregation
- `PARALLEL_MERGE`: Parallel merge aggregation
- `HIERARCHICAL`: Hierarchical aggregation
- `VOTING`: Voting aggregation
- `BEST_OF`: Best of aggregation
- `CONSENSUS`: Consensus aggregation

### 3. SubTaskResult Model

The `SubTaskResult` model defines the result of a subtask. The following fields are stable:

- `subtask_id: str`: Subtask ID
- `provider: str`: Provider name
- `result: str`: Result
- `success: bool`: Whether execution succeeded
- `error: Optional[str]`: Error message
- `execution_time: Optional[float]`: Execution time

## Stability Guarantees

- **Major versions** (e.g., 1.0 → 2.0) may introduce breaking changes to the stable API surface
- **Minor versions** (e.g., 1.0 → 1.1) will not introduce breaking changes to the stable API surface
- **Patch versions** (e.g., 1.0.0 → 1.0.1) will only include bug fixes and will not change the API surface

## Deprecation Policy

When a stable API feature is deprecated:
1. It will be marked as deprecated in the documentation
2. A deprecation warning will be added
3. The feature will be maintained for at least two minor versions before removal
4. Removal will only happen in a major version

## Extending the API

When extending the API:
1. New methods should be added as optional (with default implementations)
2. New fields should be added with default values
3. New enums should be added as new values, not replacing existing ones

## Conclusion

This document defines the stable API surface for SplitMind plugins. By following these guidelines, plugin developers can create compatible providers that will work with future versions of SplitMind.
