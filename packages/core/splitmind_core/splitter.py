"""
Task Splitter - Core module for splitting tasks into subtasks.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
import re
import json


class TaskType(str, Enum):
    ANALYSIS = "analysis"
    GENERATION = "generation"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    EXTRACTION = "extraction"
    CLASSIFICATION = "classification"
    REASONING = "reasoning"
    MIXED = "mixed"


class SubTaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SubTask(BaseModel):
    id: str
    description: str
    task_type: TaskType
    input_data: str
    original_input: Optional[str] = None
    sensitive_info: Dict[str, str] = Field(default_factory=dict)
    assigned_provider: Optional[str] = None
    status: SubTaskStatus = SubTaskStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def get_redacted_input(self) -> str:
        return self.input_data
    
    def restore_sensitive_info(self, result: str) -> str:
        restored = result
        for placeholder, original in self.sensitive_info.items():
            restored = restored.replace(placeholder, original)
        return restored


class TaskSplitResult(BaseModel):
    original_task: str
    subtasks: List[SubTask]
    task_type: TaskType
    split_strategy: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskSplitter:
    """
    Task Splitter - Analyzes and splits tasks for privacy protection.
    
    The splitter identifies sensitive information and creates subtasks
    that can be processed independently with minimal data exposure.
    """
    
    def __init__(
        self,
        enable_auto_redaction: bool = True,
        custom_patterns: Optional[List[str]] = None,
        llm_split: bool = True,
    ):
        self.enable_auto_redaction = enable_auto_redaction
        self.llm_split = llm_split
        self._sensitive_patterns = self._get_default_patterns()
        if custom_patterns:
            self._sensitive_patterns.extend(custom_patterns)
        self._counter = 0
    
    def _get_default_patterns(self) -> Dict[str, re.Pattern]:
        return {
            "phone": re.compile(r'(?<!\d)(1[3-9]\d{9})(?!\d)'),
            "email": re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w+\b'),
            "id_card": re.compile(r'\b\d{17}[\dXx]\b'),
            "bank_card": re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
            "amount": re.compile(r'(?<!\d)(?:\d{1,3}(?:,\d{3})*|\d+)(?:\.\d{2})?\s*(?:元|美元|USD|CNY|RMB|￥|\$)(?!\d)'),
            "name_cn": re.compile(r'(?<=[，。；：！？、\s])([\u4e00-\u9fa5]{2,4})(?=[，。；：！？、\s]|$)'),
        }
    
    def _generate_id(self) -> str:
        self._counter += 1
        return f"subtask_{self._counter:03d}"
    
    def detect_sensitive_info(self, text: str) -> Dict[str, List[str]]:
        detected = {}
        for info_type, pattern in self._sensitive_patterns.items():
            matches = pattern.findall(text)
            if matches:
                detected[info_type] = list(set(matches))
        return detected
    
    def redact_text(self, text: str) -> tuple[str, Dict[str, str]]:
        if not self.enable_auto_redaction:
            return text, {}
        
        redacted = text
        placeholders = {}
        
        sensitive_info = self.detect_sensitive_info(text)
        
        for info_type, items in sensitive_info.items():
            for idx, item in enumerate(items):
                placeholder = f"[REDACTED_{info_type.upper()}_{idx}]"
                placeholders[placeholder] = item
                redacted = redacted.replace(item, placeholder, 1)
        
        return redacted, placeholders
    
    def analyze_task_type(self, task: str) -> TaskType:
        task_lower = task.lower()
        
        keywords = {
            TaskType.ANALYSIS: ["分析", "analyze", "评估", "evaluate", "研究", "research"],
            TaskType.GENERATION: ["生成", "generate", "创建", "create", "写", "write", "编写"],
            TaskType.SUMMARIZATION: ["总结", "summarize", "摘要", "abstract", "概括"],
            TaskType.TRANSLATION: ["翻译", "translate", "translate"],
            TaskType.EXTRACTION: ["提取", "extract", "抽取", "获取信息"],
            TaskType.CLASSIFICATION: ["分类", "classify", "归类", "categorize"],
            TaskType.REASONING: ["推理", "reasoning", "推断", "deduce", "计算", "calculate"],
        }
        
        for task_type, words in keywords.items():
            if any(word in task_lower for word in words):
                return task_type
        
        return TaskType.MIXED
    
    def split_by_sections(self, text: str) -> List[str]:
        sections = re.split(r'\n\s*\n+', text)
        return [s.strip() for s in sections if s.strip()]
    
    def split_by_questions(self, text: str) -> List[str]:
        pattern = r'(?:(?:问题|Question|Q)\s*[\d一二三四五六七八九十]+[\.、：:]?\s*)'
        parts = re.split(pattern, text, flags=re.IGNORECASE)
        return [p.strip() for p in parts if p.strip()]
    
    def split_by_semantic_units(self, text: str) -> List[str]:
        sentences = re.split(r'(?<=[。！？\n])\s*', text)
        units = []
        current_unit = []
        
        for sentence in sentences:
            current_unit.append(sentence)
            if len(''.join(current_unit)) > 500:
                units.append(''.join(current_unit))
                current_unit = []
        
        if current_unit:
            units.append(''.join(current_unit))
        
        return [u for u in units if u.strip()]
    
    def create_subtask(
        self,
        description: str,
        input_data: str,
        task_type: TaskType,
        original_input: Optional[str] = None,
    ) -> SubTask:
        redacted_input, sensitive_info = self.redact_text(input_data)
        
        return SubTask(
            id=self._generate_id(),
            description=description,
            task_type=task_type,
            input_data=redacted_input,
            original_input=original_input or input_data,
            sensitive_info=sensitive_info,
        )
    
    def split(
        self,
        task: str,
        context: Optional[str] = None,
        strategy: str = "auto",
        max_subtasks: int = 5,
    ) -> TaskSplitResult:
        full_input = f"{context}\n\n{task}" if context else task
        
        task_type = self.analyze_task_type(task)
        
        if strategy == "auto":
            strategy = self._determine_strategy(full_input, task_type)
        
        subtasks = []
        
        if strategy == "single":
            subtask = self.create_subtask(
                description=f"Process the following {task_type.value} task",
                input_data=full_input,
                task_type=task_type,
            )
            subtasks.append(subtask)
        
        elif strategy == "section":
            sections = self.split_by_sections(full_input)
            for idx, section in enumerate(sections):
                subtask = self.create_subtask(
                    description=f"Process section {idx + 1}",
                    input_data=section,
                    task_type=task_type,
                    original_input=full_input,
                )
                subtasks.append(subtask)
        
        elif strategy == "semantic":
            units = self.split_by_semantic_units(full_input)
            for idx, unit in enumerate(units):
                subtask = self.create_subtask(
                    description=f"Process part {idx + 1}",
                    input_data=unit,
                    task_type=task_type,
                    original_input=full_input,
                )
                subtasks.append(subtask)
        
        elif strategy == "parallel":
            subtasks = self._create_parallel_subtasks(full_input, task_type, max_subtasks)
        
        if len(subtasks) > max_subtasks:
            subtasks = subtasks[:max_subtasks]
        
        return TaskSplitResult(
            original_task=task,
            subtasks=subtasks,
            task_type=task_type,
            split_strategy=strategy,
            metadata={
                "total_subtasks": len(subtasks),
                "original_length": len(full_input),
            }
        )
    
    def _determine_strategy(self, text: str, task_type: TaskType) -> str:
        if len(text) < 500:
            return "single"
        
        if task_type in [TaskType.SUMMARIZATION, TaskType.TRANSLATION]:
            if len(text) > 2000:
                return "section"
            return "single"
        
        if task_type == TaskType.ANALYSIS:
            return "parallel"
        
        if task_type == TaskType.EXTRACTION:
            return "semantic"
        
        sections = self.split_by_sections(text)
        if len(sections) > 1:
            return "section"
        
        return "semantic"
    
    def _create_parallel_subtasks(
        self,
        text: str,
        task_type: TaskType,
        max_subtasks: int,
    ) -> List[SubTask]:
        subtasks = []
        
        subtask_types = [
            ("Extract key information", TaskType.EXTRACTION),
            ("Analyze structure and patterns", TaskType.ANALYSIS),
            ("Identify sensitive content", TaskType.CLASSIFICATION),
            ("Generate summary", TaskType.SUMMARIZATION),
            ("Provide recommendations", TaskType.GENERATION),
        ]
        
        for idx, (desc, st_type) in enumerate(subtask_types[:max_subtasks]):
            subtask = self.create_subtask(
                description=desc,
                input_data=text,
                task_type=st_type,
            )
            subtasks.append(subtask)
        
        return subtasks
    
    def split_with_llm(
        self,
        task: str,
        context: Optional[str] = None,
        llm_client: Optional[Any] = None,
    ) -> TaskSplitResult:
        if llm_client is None:
            return self.split(task, context, strategy="auto")
        
        prompt = f"""Analyze the following task and split it into independent subtasks for privacy-preserving processing.

Task: {task}
Context: {context or "None"}

Please output a JSON with the following structure:
{{
    "task_type": "analysis|generation|summarization|translation|extraction|classification|reasoning|mixed",
    "subtasks": [
        {{
            "description": "What this subtask should do",
            "input_subset": "The specific part of input this subtask needs",
            "task_type": "the type of this subtask"
        }}
    ],
    "split_strategy": "single|section|semantic|parallel",
    "reasoning": "Why this split strategy was chosen"
}}

Output only the JSON, no other text."""

        try:
            response = llm_client.generate(prompt)
            result = json.loads(response)
            
            task_type = TaskType(result.get("task_type", "mixed"))
            subtasks = []
            
            for idx, st in enumerate(result.get("subtasks", [])):
                redacted, placeholders = self.redact_text(st.get("input_subset", task))
                subtask = SubTask(
                    id=f"subtask_{idx:03d}",
                    description=st.get("description", ""),
                    task_type=TaskType(st.get("task_type", "mixed")),
                    input_data=redacted,
                    sensitive_info=placeholders,
                )
                subtasks.append(subtask)
            
            return TaskSplitResult(
                original_task=task,
                subtasks=subtasks,
                task_type=task_type,
                split_strategy=result.get("split_strategy", "auto"),
                metadata={"reasoning": result.get("reasoning", "")},
            )
        except Exception:
            return self.split(task, context, strategy="auto")
