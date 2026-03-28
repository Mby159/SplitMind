#!/usr/bin/env python3
"""
Mock Local Model Interface
Simulates a local model for testing purposes without requiring Ollama.
"""

from typing import Optional, Dict, Any, List
from splitmind.core.local_model import LocalModelInterface, LocalModelConfig, LocalModelBackend


class MockLocalModelInterface(LocalModelInterface):
    """Mock local model interface for testing."""
    
    def __init__(self, config: Optional[LocalModelConfig] = None):
        super().__init__(config)
        # Override availability to True for testing
        self._is_available = True
    
    def _test_connection(self):
        """Mock connection test."""
        self._is_available = True
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Mock text generation."""
        if not self._is_available:
            raise RuntimeError("Local model is not available")
        
        # Simple mock responses based on prompt content
        if "总结" in prompt or "summarize" in prompt.lower():
            return "人工智能的主要应用领域包括：1. 自然语言处理（如聊天机器人、翻译）2. 计算机视觉（如图像识别、物体检测）3. 语音识别与合成 4. 推荐系统 5. 自动驾驶 6. 医疗诊断 7. 金融分析 8. 教育辅助。这些应用正在改变各个行业的运作方式，提高效率和准确性。"
        elif "分析" in prompt or "analyze" in prompt.lower():
            return "分析结果：用户反馈整体积极，主要关注点在于产品的易用性和功能完整性。建议：1. 优化用户界面设计 2. 增加更多个性化功能 3. 提高系统响应速度 4. 加强数据安全保护。通过这些改进，可以进一步提升用户满意度和产品竞争力。"
        elif "隐私" in prompt or "privacy" in prompt.lower():
            return "隐私保护建议：1. 采用端侧处理，减少数据传输 2. 实施数据加密 3. 最小化数据收集 4. 提供用户数据控制选项 5. 定期进行安全审计。这些措施可以有效保护用户隐私，增强用户信任。"
        else:
            return f"这是模拟本地模型对以下提示的响应：{prompt[:100]}..."
    
    def classify(self, text: str, categories: List[str]) -> Dict[str, float]:
        """Mock text classification."""
        # Simple mock classification
        return {cat: 1.0 / len(categories) for cat in categories}
    
    def detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """Mock PII detection."""
        # Simple mock PII detection
        import re
        results = []
        
        # Mock phone detection
        phone_pattern = r'1[3-9]\d{9}'
        for match in re.finditer(phone_pattern, text):
            results.append({
                "type": "phone",
                "value": match.group(),
                "confidence": 0.95
            })
        
        # Mock email detection
        email_pattern = r'[\w._%+-]+@[\w.-]+\.\w+'
        for match in re.finditer(email_pattern, text):
            results.append({
                "type": "email",
                "value": match.group(),
                "confidence": 0.98
            })
        
        return results
    
    def analyze_task(self, task: str) -> Dict[str, Any]:
        """Mock task analysis."""
        # Simple mock task analysis
        if "总结" in task or "summarize" in task.lower():
            return {
                "task_type": "summarization",
                "complexity": "medium",
                "requires_context": False,
                "recommended_strategy": "single"
            }
        elif "分析" in task or "analyze" in task.lower():
            return {
                "task_type": "analysis",
                "complexity": "high",
                "requires_context": True,
                "recommended_strategy": "parallel"
            }
        elif "翻译" in task or "translate" in task.lower():
            return {
                "task_type": "translation",
                "complexity": "medium",
                "requires_context": False,
                "recommended_strategy": "single"
            }
        else:
            return {
                "task_type": "mixed",
                "complexity": "medium",
                "requires_context": True,
                "recommended_strategy": "semantic"
            }
    
    def merge_results(self, results: List[str], context: Optional[str] = None) -> str:
        """Mock result merging."""
        return "\n\n".join(results)
    
    def detect_conflicts(self, results: List[str]) -> List[Dict[str, Any]]:
        """Mock conflict detection."""
        return []
