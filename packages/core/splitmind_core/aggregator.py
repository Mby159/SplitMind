"""
Result Aggregator - Aggregates results from multiple AI providers.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
import re
from datetime import datetime


class AggregationStrategy(str, Enum):
    SEQUENTIAL = "sequential"
    PARALLEL_MERGE = "parallel_merge"
    HIERARCHICAL = "hierarchical"
    VOTING = "voting"
    BEST_OF = "best_of"


class SubTaskResult(BaseModel):
    subtask_id: str
    provider: str
    result: str
    success: bool = True
    error: Optional[str] = None
    execution_time: Optional[float] = None
    tokens_used: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AggregatedResult(BaseModel):
    final_result: str
    subtask_results: List[SubTaskResult]
    aggregation_strategy: AggregationStrategy
    total_execution_time: float
    providers_used: List[str]
    confidence_score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ResultAggregator:
    """
    Result Aggregator - Combines and synthesizes results from multiple AI providers.
    
    Supports various aggregation strategies:
    - Sequential: Chain results in order
    - Parallel Merge: Combine independent results
    - Hierarchical: Use one result to enhance another
    - Voting: Select best answer through consensus
    - Best Of: Pick the highest quality result
    """
    
    def __init__(
        self,
        default_strategy: AggregationStrategy = AggregationStrategy.PARALLEL_MERGE,
        llm_client: Optional[Any] = None,
    ):
        self.default_strategy = default_strategy
        self.llm_client = llm_client
    
    def aggregate(
        self,
        results: List[SubTaskResult],
        strategy: Optional[AggregationStrategy] = None,
        context: Optional[str] = None,
    ) -> AggregatedResult:
        if not results:
            return AggregatedResult(
                final_result="",
                subtask_results=[],
                aggregation_strategy=strategy or self.default_strategy,
                total_execution_time=0.0,
                providers_used=[],
            )
        
        strategy = strategy or self.default_strategy
        
        successful_results = [r for r in results if r.success]
        if not successful_results:
            errors = [r.error for r in results if r.error]
            return AggregatedResult(
                final_result=f"All subtasks failed. Errors: {'; '.join(errors)}",
                subtask_results=results,
                aggregation_strategy=strategy,
                total_execution_time=0.0,
                providers_used=[],
            )
        
        start_time = datetime.now()
        
        if strategy == AggregationStrategy.SEQUENTIAL:
            final = self._aggregate_sequential(successful_results, context)
        elif strategy == AggregationStrategy.PARALLEL_MERGE:
            final = self._aggregate_parallel_merge(successful_results, context)
        elif strategy == AggregationStrategy.HIERARCHICAL:
            final = self._aggregate_hierarchical(successful_results, context)
        elif strategy == AggregationStrategy.VOTING:
            final = self._aggregate_voting(successful_results, context)
        elif strategy == AggregationStrategy.BEST_OF:
            final = self._aggregate_best_of(successful_results, context)
        else:
            final = self._aggregate_parallel_merge(successful_results, context)
        
        total_time = sum(
            r.execution_time for r in successful_results 
            if r.execution_time is not None
        )
        
        providers = list(set(r.provider for r in successful_results))
        
        confidence = self._calculate_confidence(successful_results)
        
        return AggregatedResult(
            final_result=final,
            subtask_results=results,
            aggregation_strategy=strategy,
            total_execution_time=total_time,
            providers_used=providers,
            confidence_score=confidence,
        )
    
    def _aggregate_sequential(
        self,
        results: List[SubTaskResult],
        context: Optional[str],
    ) -> str:
        parts = []
        
        for result in results:
            parts.append(f"### {result.subtask_id}\n\n{result.result}")
        
        return "\n\n".join(parts)
    
    def _aggregate_parallel_merge(
        self,
        results: List[SubTaskResult],
        context: Optional[str],
    ) -> str:
        if len(results) == 1:
            return results[0].result
        
        if self.llm_client:
            return self._llm_merge(results, context)
        
        return self._rule_based_merge(results)
    
    def _aggregate_hierarchical(
        self,
        results: List[SubTaskResult],
        context: Optional[str],
    ) -> str:
        if len(results) == 1:
            return results[0].result
        
        sorted_results = sorted(
            results,
            key=lambda r: len(r.result),
            reverse=True,
        )
        
        base_result = sorted_results[0].result
        
        enhancements = []
        for result in sorted_results[1:]:
            unique_info = self._extract_unique_info(base_result, result.result)
            if unique_info:
                enhancements.append(unique_info)
        
        if enhancements:
            return f"{base_result}\n\n**Additional Insights:**\n" + "\n".join(f"- {e}" for e in enhancements)
        
        return base_result
    
    def _aggregate_voting(
        self,
        results: List[SubTaskResult],
        context: Optional[str],
    ) -> str:
        if len(results) == 1:
            return results[0].result
        
        key_points = {}
        
        for result in results:
            sentences = self._extract_key_sentences(result.result)
            for sentence in sentences:
                normalized = self._normalize_sentence(sentence)
                if normalized not in key_points:
                    key_points[normalized] = {"count": 0, "original": sentence}
                key_points[normalized]["count"] += 1
        
        consensus_points = [
            kp["original"] for kp in key_points.values()
            if kp["count"] >= max(2, len(results) // 2)
        ]
        
        if consensus_points:
            return "Key findings:\n" + "\n".join(f"- {p}" for p in consensus_points)
        
        return self._aggregate_best_of(results, context)
    
    def _aggregate_best_of(
        self,
        results: List[SubTaskResult],
        context: Optional[str],
    ) -> str:
        if len(results) == 1:
            return results[0].result
        
        best_result = max(results, key=lambda r: self._score_result(r.result))
        return best_result.result
    
    def _llm_merge(
        self,
        results: List[SubTaskResult],
        context: Optional[str],
    ) -> str:
        results_text = "\n\n".join(
            f"Source: {r.provider}\nResult: {r.result}"
            for r in results
        )
        
        prompt = f"""Please synthesize the following results from multiple AI providers into a coherent, comprehensive response.

Context: {context or "Not provided"}

Results:
{results_text}

Please provide a unified response that:
1. Combines all relevant information
2. Resolves any contradictions
3. Presents the information clearly and concisely

Synthesized response:"""
        
        try:
            return self.llm_client.generate(prompt)
        except Exception:
            return self._rule_based_merge(results)
    
    def _rule_based_merge(self, results: List[SubTaskResult]) -> str:
        merged_sections = {}
        
        for result in results:
            sections = self._split_into_sections(result.result)
            for title, content in sections.items():
                if title not in merged_sections:
                    merged_sections[title] = []
                merged_sections[title].append(content)
        
        output = []
        for title, contents in merged_sections.items():
            if len(contents) == 1:
                output.append(f"## {title}\n{contents[0]}")
            else:
                combined = self._combine_contents(contents)
                output.append(f"## {title}\n{combined}")
        
        return "\n\n".join(output)
    
    def _split_into_sections(self, text: str) -> Dict[str, str]:
        sections = {}
        current_title = "Main"
        current_content = []
        
        for line in text.split("\n"):
            if line.startswith("##") or line.startswith("**"):
                if current_content:
                    sections[current_title] = "\n".join(current_content).strip()
                current_title = line.lstrip("#* ").strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_content:
            sections[current_title] = "\n".join(current_content).strip()
        
        return sections
    
    def _combine_contents(self, contents: List[str]) -> str:
        unique_sentences = set()
        combined = []
        
        for content in contents:
            for sentence in content.split(". "):
                normalized = sentence.lower().strip()
                if normalized and normalized not in unique_sentences:
                    unique_sentences.add(normalized)
                    combined.append(sentence.strip())
        
        return ". ".join(combined)
    
    def _extract_key_sentences(self, text: str) -> List[str]:
        sentences = re.split(r'[。！？.!?]', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def _normalize_sentence(self, sentence: str) -> str:
        normalized = sentence.lower().strip()
        normalized = re.sub(r'\s+', ' ', normalized)
        normalized = re.sub(r'[^\w\s\u4e00-\u9fa5]', '', normalized)
        return normalized
    
    def _extract_unique_info(self, base: str, additional: str) -> Optional[str]:
        base_sentences = set(self._extract_key_sentences(base))
        additional_sentences = self._extract_key_sentences(additional)
        
        unique = [
            s for s in additional_sentences
            if self._normalize_sentence(s) not in base_sentences
        ]
        
        if unique:
            return "; ".join(unique[:3])
        return None
    
    def _score_result(self, text: str) -> float:
        score = 0.0
        
        score += min(len(text) / 100, 10)
        
        score += text.count("。") + text.count(".")
        
        if "首先" in text or "first" in text.lower():
            score += 1
        if "其次" in text or "second" in text.lower():
            score += 1
        if "最后" in text or "finally" in text.lower():
            score += 1
        if "总之" in text or "conclusion" in text.lower():
            score += 1
        
        score += text.count("\n") * 0.5
        
        return score
    
    def _calculate_confidence(self, results: List[SubTaskResult]) -> float:
        if not results:
            return 0.0
        
        success_rate = len(results) / max(len(results), 1)
        
        provider_diversity = len(set(r.provider for r in results)) / max(len(results), 1)
        
        avg_length = sum(len(r.result) for r in results) / len(results)
        length_score = min(avg_length / 500, 1.0)
        
        confidence = (
            success_rate * 0.4 +
            provider_diversity * 0.3 +
            length_score * 0.3
        )
        
        return round(confidence, 2)
    
    def restore_sensitive_info(
        self,
        result: str,
        sensitive_mappings: Dict[str, str],
    ) -> str:
        restored = result
        for placeholder, original in sensitive_mappings.items():
            restored = restored.replace(placeholder, original)
        return restored
    
    def create_summary(
        self,
        aggregated_result: AggregatedResult,
        include_metadata: bool = True,
    ) -> str:
        lines = ["# Task Execution Summary\n"]
        
        lines.append("## Final Result\n")
        lines.append(aggregated_result.final_result)
        
        if include_metadata:
            lines.append("\n## Execution Details\n")
            lines.append(f"- Strategy: {aggregated_result.aggregation_strategy.value}")
            lines.append(f"- Providers used: {', '.join(aggregated_result.providers_used)}")
            lines.append(f"- Total time: {aggregated_result.total_execution_time:.2f}s")
            if aggregated_result.confidence_score:
                lines.append(f"- Confidence: {aggregated_result.confidence_score:.0%}")
            
            lines.append("\n## Subtask Results\n")
            for r in aggregated_result.subtask_results:
                status = "✓" if r.success else "✗"
                lines.append(f"- {status} {r.subtask_id} ({r.provider})")
        
        return "\n".join(lines)
