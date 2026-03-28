"""
Result Aggregator - Aggregates results from multiple AI providers.
Enhanced version with conflict detection and advanced quality assessment.
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from pydantic import BaseModel, Field
from enum import Enum
import re
from datetime import datetime
from dataclasses import dataclass


class AggregationStrategy(str, Enum):
    SEQUENTIAL = "sequential"
    PARALLEL_MERGE = "parallel_merge"
    HIERARCHICAL = "hierarchical"
    VOTING = "voting"
    BEST_OF = "best_of"
    CONSENSUS = "consensus"  # New: Find consensus among results


class ResultQuality(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    FAILED = "failed"


class SubTaskResult(BaseModel):
    subtask_id: str
    provider: str
    result: str
    success: bool = True
    error: Optional[str] = None
    execution_time: Optional[float] = None
    tokens_used: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Enhanced fields for quality assessment
    quality_score: Optional[float] = None
    quality_rating: Optional[ResultQuality] = None
    confidence: Optional[float] = None


class AggregatedResult(BaseModel):
    final_result: str
    subtask_results: List[SubTaskResult]
    aggregation_strategy: AggregationStrategy
    total_execution_time: float
    providers_used: List[str]
    confidence_score: Optional[float] = None
    
    # Enhanced fields
    quality_assessment: Dict[str, Any] = Field(default_factory=dict)
    conflicts_detected: List[Dict[str, Any]] = Field(default_factory=list)
    consensus_info: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


@dataclass
class ConflictInfo:
    """Represents a conflict between results."""
    conflict_type: str  # 'contradiction', 'inconsistency', 'omission'
    description: str
    involved_results: List[str]  # subtask_ids
    severity: str  # 'high', 'medium', 'low'
    suggested_resolution: Optional[str] = None


@dataclass
class QualityMetrics:
    """Quality metrics for a result."""
    completeness: float  # 0-1
    coherence: float  # 0-1
    relevance: float  # 0-1
    accuracy: float  # 0-1
    overall_score: float  # 0-1


class ResultAggregator:
    """
    Result Aggregator - Combines and synthesizes results from multiple AI providers.
    
    Enhanced features:
    - Advanced quality assessment
    - Conflict detection and resolution
    - Consensus-based aggregation
    - Multi-dimensional result scoring
    
    Supports various aggregation strategies:
    - Sequential: Chain results in order
    - Parallel Merge: Combine independent results
    - Hierarchical: Use one result to enhance another
    - Voting: Select best answer through consensus
    - Best Of: Pick the highest quality result
    - Consensus: Find common ground among results
    """
    
    # Quality assessment weights
    QUALITY_WEIGHTS = {
        "length": 0.15,
        "structure": 0.20,
        "content": 0.35,
        "consistency": 0.30,
    }
    
    def __init__(
        self,
        default_strategy: AggregationStrategy = AggregationStrategy.PARALLEL_MERGE,
        llm_client: Optional[Any] = None,
        enable_conflict_detection: bool = True,
        enable_quality_assessment: bool = True,
        min_quality_threshold: float = 0.5,
    ):
        self.default_strategy = default_strategy
        self.llm_client = llm_client
        self.enable_conflict_detection = enable_conflict_detection
        self.enable_quality_assessment = enable_quality_assessment
        self.min_quality_threshold = min_quality_threshold
    
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
        
        # Assess quality if enabled
        if self.enable_quality_assessment:
            results = self._assess_results_quality(results)
        
        # Filter out poor quality results
        successful_results = [
            r for r in results 
            if r.success and (r.quality_score or 0.5) >= self.min_quality_threshold
        ]
        
        if not successful_results:
            errors = [r.error for r in results if r.error]
            return AggregatedResult(
                final_result=f"All subtasks failed or produced poor quality results. Errors: {'; '.join(errors)}",
                subtask_results=results,
                aggregation_strategy=strategy,
                total_execution_time=0.0,
                providers_used=[],
                quality_assessment={"status": "all_failed"},
            )
        
        # Detect conflicts if enabled
        conflicts = []
        if self.enable_conflict_detection and len(successful_results) > 1:
            conflicts = self._detect_conflicts(successful_results)
        
        start_time = datetime.now()
        
        # Apply aggregation strategy
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
        elif strategy == AggregationStrategy.CONSENSUS:
            final = self._aggregate_consensus(successful_results, context)
        else:
            final = self._aggregate_parallel_merge(successful_results, context)
        
        total_time = sum(
            r.execution_time for r in successful_results 
            if r.execution_time is not None
        )
        
        providers = list(set(r.provider for r in successful_results))
        
        confidence = self._calculate_confidence(successful_results, conflicts)
        
        # Generate quality assessment
        quality_assessment = self._generate_quality_assessment(successful_results)
        
        # Generate consensus info
        consensus_info = self._generate_consensus_info(successful_results, conflicts)
        
        return AggregatedResult(
            final_result=final,
            subtask_results=results,
            aggregation_strategy=strategy,
            total_execution_time=total_time,
            providers_used=providers,
            confidence_score=confidence,
            quality_assessment=quality_assessment,
            conflicts_detected=[self._conflict_to_dict(c) for c in conflicts],
            consensus_info=consensus_info,
        )
    
    def _assess_results_quality(self, results: List[SubTaskResult]) -> List[SubTaskResult]:
        """Assess quality of each result."""
        for result in results:
            if not result.success:
                result.quality_score = 0.0
                result.quality_rating = ResultQuality.FAILED
                continue
            
            metrics = self._calculate_quality_metrics(result.result)
            result.quality_score = metrics.overall_score
            
            # Assign quality rating
            if metrics.overall_score >= 0.85:
                result.quality_rating = ResultQuality.EXCELLENT
            elif metrics.overall_score >= 0.70:
                result.quality_rating = ResultQuality.GOOD
            elif metrics.overall_score >= 0.50:
                result.quality_rating = ResultQuality.FAIR
            else:
                result.quality_rating = ResultQuality.POOR
            
            result.confidence = metrics.accuracy
        
        return results
    
    def _calculate_quality_metrics(self, text: str) -> QualityMetrics:
        """Calculate comprehensive quality metrics for a result."""
        # Length score
        length_score = min(len(text) / 500, 1.0) if len(text) < 2000 else 0.9
        
        # Structure score
        structure_score = self._assess_structure(text)
        
        # Content score
        content_score = self._assess_content(text)
        
        # Consistency score
        consistency_score = self._assess_consistency(text)
        
        # Calculate overall score
        overall = (
            length_score * self.QUALITY_WEIGHTS["length"] +
            structure_score * self.QUALITY_WEIGHTS["structure"] +
            content_score * self.QUALITY_WEIGHTS["content"] +
            consistency_score * self.QUALITY_WEIGHTS["consistency"]
        )
        
        return QualityMetrics(
            completeness=length_score,
            coherence=consistency_score,
            relevance=content_score,
            accuracy=structure_score,
            overall_score=overall,
        )
    
    def _assess_structure(self, text: str) -> float:
        """Assess structural quality of text."""
        score = 0.5
        
        # Check for proper paragraphing
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        if len(paragraphs) >= 2:
            score += 0.15
        
        # Check for headings or sections
        if re.search(r'#{1,3}\s+\w+|^\*\*[^*]+\*\*', text, re.MULTILINE):
            score += 0.15
        
        # Check for lists
        if re.search(r'^\s*[-•*\d]\s+', text, re.MULTILINE):
            score += 0.1
        
        # Check for proper sentence structure
        sentences = re.split(r'[。！？.!?]', text)
        avg_sentence_length = sum(len(s) for s in sentences) / max(len(sentences), 1)
        if 20 <= avg_sentence_length <= 200:
            score += 0.1
        
        return min(1.0, score)
    
    def _assess_content(self, text: str) -> float:
        """Assess content quality."""
        score = 0.5
        
        # Check for informative content indicators
        indicators = [
            "首先", "其次", "最后", "第一", "第二", "第三",
            "first", "second", "third", "finally", "additionally",
            "例如", "比如", "for example", "such as",
            "因此", "所以", "thus", "therefore",
            "总结", "结论", "in conclusion", "summary",
        ]
        indicator_count = sum(1 for ind in indicators if ind in text.lower())
        score += min(0.3, indicator_count * 0.03)
        
        # Check for specific information (numbers, dates, etc.)
        if re.search(r'\d{4}年|\d{1,2}月|\d{1,2}日', text):
            score += 0.1
        
        # Check for diverse vocabulary
        words = set(re.findall(r'\b[\u4e00-\u9fa5a-zA-Z]{2,}\b', text))
        if len(words) > 50:
            score += 0.1
        
        return min(1.0, score)
    
    def _assess_consistency(self, text: str) -> float:
        """Assess internal consistency of text."""
        score = 0.7
        
        # Check for contradictions
        contradiction_patterns = [
            (r'是\s*.{0,10}\s*不是', r'不是\s*.{0,10}\s*是'),
            (r'可以\s*.{0,10}\s*不能', r'不能\s*.{0,10}\s*可以'),
            (r'有\s*.{0,10}\s*没有', r'没有\s*.{0,10}\s*有'),
        ]
        
        for pattern1, pattern2 in contradiction_patterns:
            if re.search(pattern1, text) and re.search(pattern2, text):
                score -= 0.1
        
        # Check for consistent tense/structure
        lines = text.split('\n')
        if len(lines) > 3:
            # Check if structure is consistent
            first_line_pattern = re.match(r'^(\s*[-•*\d]\s+)', lines[0])
            consistent_lines = sum(
                1 for line in lines[1:] 
                if bool(re.match(r'^(\s*[-•*\d]\s+)', line)) == bool(first_line_pattern)
            )
            if consistent_lines / max(len(lines) - 1, 1) > 0.8:
                score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _detect_conflicts(self, results: List[SubTaskResult]) -> List[ConflictInfo]:
        """Detect conflicts between results."""
        conflicts = []
        
        # Extract key facts from each result
        facts_by_result = {}
        for result in results:
            facts_by_result[result.subtask_id] = self._extract_key_facts(result.result)
        
        # Compare facts between results
        result_ids = list(facts_by_result.keys())
        for i, id1 in enumerate(result_ids):
            for id2 in result_ids[i+1:]:
                conflicts.extend(
                    self._compare_facts(id1, facts_by_result[id1], id2, facts_by_result[id2])
                )
        
        return conflicts
    
    def _extract_key_facts(self, text: str) -> List[Dict[str, str]]:
        """Extract key facts from text."""
        facts = []
        
        # Extract statements with numbers
        number_patterns = [
            r'(?:\d+(?:\.\d+)?)\s*(?:%|percent|百分比)',
            r'(?:\d{4})年',
            r'(?:\d+)个',
            r'(?:\d+)次',
        ]
        for pattern in number_patterns:
            for match in re.finditer(pattern, text):
                # Get surrounding context
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                context = text[start:end]
                facts.append({
                    "type": "numerical",
                    "value": match.group(),
                    "context": context,
                })
        
        # Extract named entities (simplified)
        entity_patterns = [
            r'(?:公司|企业|组织)\s*["\']?([^"\']{2,20})["\']?',
            r'(?:产品|服务)\s*["\']?([^"\']{2,20})["\']?',
        ]
        for pattern in entity_patterns:
            for match in re.finditer(pattern, text):
                facts.append({
                    "type": "entity",
                    "value": match.group(1),
                    "context": match.group(),
                })
        
        return facts
    
    def _compare_facts(
        self, 
        id1: str, 
        facts1: List[Dict[str, str]], 
        id2: str, 
        facts2: List[Dict[str, str]]
    ) -> List[ConflictInfo]:
        """Compare facts between two results to find conflicts."""
        conflicts = []
        
        # Check for contradictory numerical values
        for fact1 in facts1:
            if fact1["type"] != "numerical":
                continue
            
            for fact2 in facts2:
                if fact2["type"] != "numerical":
                    continue
                
                # Check if they refer to the same thing but have different values
                if (self._similar_context(fact1["context"], fact2["context"]) and
                    fact1["value"] != fact2["value"]):
                    conflicts.append(ConflictInfo(
                        conflict_type="contradiction",
                        description=f"Contradictory values: '{fact1['value']}' vs '{fact2['value']}'",
                        involved_results=[id1, id2],
                        severity="high",
                        suggested_resolution="Review both sources and verify the correct value",
                    ))
        
        return conflicts
    
    def _similar_context(self, ctx1: str, ctx2: str) -> bool:
        """Check if two contexts are similar."""
        # Simple similarity check based on common words
        words1 = set(re.findall(r'\b[\u4e00-\u9fa5a-zA-Z]{2,}\b', ctx1.lower()))
        words2 = set(re.findall(r'\b[\u4e00-\u9fa5a-zA-Z]{2,}\b', ctx2.lower()))
        
        if not words1 or not words2:
            return False
        
        intersection = words1 & words2
        union = words1 | words2
        similarity = len(intersection) / len(union)
        
        return similarity > 0.5
    
    def _conflict_to_dict(self, conflict: ConflictInfo) -> Dict[str, Any]:
        """Convert ConflictInfo to dictionary."""
        return {
            "conflict_type": conflict.conflict_type,
            "description": conflict.description,
            "involved_results": conflict.involved_results,
            "severity": conflict.severity,
            "suggested_resolution": conflict.suggested_resolution,
        }
    
    def _generate_quality_assessment(self, results: List[SubTaskResult]) -> Dict[str, Any]:
        """Generate overall quality assessment."""
        if not results:
            return {"status": "no_results"}
        
        quality_scores = [r.quality_score for r in results if r.quality_score is not None]
        
        return {
            "status": "assessed",
            "average_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            "best_quality": max(quality_scores) if quality_scores else 0,
            "worst_quality": min(quality_scores) if quality_scores else 0,
            "excellent_results": sum(1 for r in results if r.quality_rating == ResultQuality.EXCELLENT),
            "good_results": sum(1 for r in results if r.quality_rating == ResultQuality.GOOD),
            "fair_results": sum(1 for r in results if r.quality_rating == ResultQuality.FAIR),
            "poor_results": sum(1 for r in results if r.quality_rating == ResultQuality.POOR),
        }
    
    def _generate_consensus_info(
        self, 
        results: List[SubTaskResult], 
        conflicts: List[ConflictInfo]
    ) -> Dict[str, Any]:
        """Generate consensus information."""
        if len(results) < 2:
            return {"status": "single_result"}
        
        # Calculate consensus score
        total_pairs = len(results) * (len(results) - 1) / 2
        conflict_count = len(conflicts)
        consensus_score = 1.0 - (conflict_count / max(total_pairs, 1))
        
        return {
            "status": "analyzed",
            "consensus_score": round(consensus_score, 2),
            "total_results": len(results),
            "conflicts_found": conflict_count,
            "agreement_level": "high" if consensus_score > 0.8 else "medium" if consensus_score > 0.5 else "low",
        }
    
    def _aggregate_sequential(
        self,
        results: List[SubTaskResult],
        context: Optional[str],
    ) -> str:
        """Sequential aggregation with quality weighting."""
        parts = []
        
        # Sort by quality score if available
        sorted_results = sorted(
            results, 
            key=lambda r: r.quality_score or 0.5, 
            reverse=True
        )
        
        for result in sorted_results:
            quality_indicator = ""
            if result.quality_rating == ResultQuality.EXCELLENT:
                quality_indicator = " [高质量]"
            elif result.quality_rating == ResultQuality.POOR:
                quality_indicator = " [需审核]"
            
            parts.append(f"### {result.subtask_id}{quality_indicator}\n\n{result.result}")
        
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
        
        # Sort by quality score
        sorted_results = sorted(
            results,
            key=lambda r: r.quality_score or 0.5,
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
                    key_points[normalized] = {"count": 0, "original": sentence, "quality": 0}
                key_points[normalized]["count"] += 1
                key_points[normalized]["quality"] += result.quality_score or 0.5
        
        # Weight by both count and quality
        for kp in key_points.values():
            kp["score"] = kp["count"] * (1 + kp["quality"] / len(results))
        
        consensus_points = [
            kp["original"] for kp in sorted(key_points.values(), key=lambda x: x["score"], reverse=True)
            if kp["count"] >= max(2, len(results) // 2)
        ]
        
        if consensus_points:
            return "Key findings:\n" + "\n".join(f"- {p}" for p in consensus_points[:10])
        
        return self._aggregate_best_of(results, context)
    
    def _aggregate_best_of(
        self,
        results: List[SubTaskResult],
        context: Optional[str],
    ) -> str:
        if len(results) == 1:
            return results[0].result
        
        # Use quality score as primary criteria
        best_result = max(results, key=lambda r: (r.quality_score or 0.5, self._score_result(r.result)))
        return best_result.result
    
    def _aggregate_consensus(
        self,
        results: List[SubTaskResult],
        context: Optional[str],
    ) -> str:
        """New: Consensus-based aggregation."""
        if len(results) == 1:
            return results[0].result
        
        # Find common elements across all results
        common_elements = self._find_common_elements([r.result for r in results])
        
        if common_elements:
            return "Consensus findings:\n\n" + "\n\n".join(common_elements)
        
        # Fall back to voting if no clear consensus
        return self._aggregate_voting(results, context)
    
    def _find_common_elements(self, texts: List[str]) -> List[str]:
        """Find common elements across multiple texts."""
        if not texts:
            return []
        
        # Extract key sentences from each text
        all_sentences = [set(self._extract_key_sentences(text)) for text in texts]
        
        # Find sentences that appear in majority of texts
        common = set()
        for sentences in all_sentences:
            for sentence in sentences:
                normalized = self._normalize_sentence(sentence)
                matches = sum(
                    1 for other_sentences in all_sentences
                    if any(self._normalize_sentence(s) == normalized for s in other_sentences)
                )
                if matches >= len(texts) // 2 + 1:
                    common.add(sentence)
        
        return list(common)[:10]
    
    def _llm_merge(
        self,
        results: List[SubTaskResult],
        context: Optional[str],
    ) -> str:
        results_text = "\n\n".join(
            f"Source: {r.provider} (Quality: {r.quality_rating.value if r.quality_rating else 'unknown'})\nResult: {r.result}"
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
4. Prioritizes high-quality sources

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
                merged_sections[title].append((content, result.quality_score or 0.5))
        
        output = []
        for title, contents in merged_sections.items():
            if len(contents) == 1:
                output.append(f"## {title}\n{contents[0][0]}")
            else:
                # Weight by quality score
                combined = self._combine_contents_weighted(contents)
                output.append(f"## {title}\n{combined}")
        
        return "\n\n".join(output)
    
    def _combine_contents_weighted(self, contents: List[Tuple[str, float]]) -> str:
        """Combine contents weighted by quality score."""
        unique_sentences = {}
        
        for content, weight in contents:
            for sentence in content.split(". "):
                normalized = sentence.lower().strip()
                if normalized:
                    if normalized not in unique_sentences:
                        unique_sentences[normalized] = {"sentence": sentence, "weight": 0}
                    unique_sentences[normalized]["weight"] += weight
        
        # Sort by weight and return top sentences
        sorted_sentences = sorted(
            unique_sentences.values(), 
            key=lambda x: x["weight"], 
            reverse=True
        )
        
        return ". ".join(s["sentence"] for s in sorted_sentences[:20])
    
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
    
    def _calculate_confidence(
        self, 
        results: List[SubTaskResult],
        conflicts: List[ConflictInfo],
    ) -> float:
        if not results:
            return 0.0
        
        # Base confidence on success rate and quality
        success_rate = len([r for r in results if r.success]) / max(len(results), 1)
        avg_quality = sum(r.quality_score or 0.5 for r in results) / len(results)
        
        provider_diversity = len(set(r.provider for r in results)) / max(len(results), 1)
        
        # Reduce confidence if conflicts exist
        conflict_penalty = len(conflicts) * 0.1
        
        confidence = (
            success_rate * 0.3 +
            avg_quality * 0.4 +
            provider_diversity * 0.2 -
            conflict_penalty
        )
        
        return round(max(0.0, min(1.0, confidence)), 2)
    
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
            
            # Quality assessment
            if aggregated_result.quality_assessment:
                qa = aggregated_result.quality_assessment
                lines.append(f"\n## Quality Assessment\n")
                lines.append(f"- Average quality: {qa.get('average_quality', 0):.0%}")
                lines.append(f"- Excellent results: {qa.get('excellent_results', 0)}")
                lines.append(f"- Good results: {qa.get('good_results', 0)}")
            
            # Conflicts
            if aggregated_result.conflicts_detected:
                lines.append(f"\n## Conflicts Detected\n")
                for conflict in aggregated_result.conflicts_detected:
                    lines.append(f"- [{conflict['severity'].upper()}] {conflict['description']}")
            
            lines.append("\n## Subtask Results\n")
            for r in aggregated_result.subtask_results:
                status = "✓" if r.success else "✗"
                quality = f" ({r.quality_rating.value})" if r.quality_rating else ""
                lines.append(f"- {status} {r.subtask_id} ({r.provider}){quality}")
        
        return "\n".join(lines)
