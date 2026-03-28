"""
Tests for SplitMind core modules.
"""

import pytest
from splitmind.core.splitter import TaskSplitter, TaskType
from splitmind.core.privacy import PrivacyHandler, RiskLevel
from splitmind.core.aggregator import ResultAggregator, SubTaskResult, AggregationStrategy


class TestTaskSplitter:
    
    def setup_method(self):
        self.splitter = TaskSplitter()
    
    def test_detect_phone_numbers(self):
        text = "请联系张三，电话：13812345678"
        detected = self.splitter.detect_sensitive_info(text)
        assert "phone" in detected
        assert "13812345678" in detected["phone"]
    
    def test_detect_email(self):
        text = "发送邮件到 test@example.com"
        detected = self.splitter.detect_sensitive_info(text)
        assert "email" in detected
        assert "test@example.com" in detected["email"]
    
    def test_detect_id_card(self):
        text = "身份证号：320123199001011234"
        detected = self.splitter.detect_sensitive_info(text)
        assert "id_card" in detected
    
    def test_redact_text(self):
        text = "张三的电话是13812345678，邮箱是test@example.com"
        redacted, mapping = self.splitter.redact_text(text)
        
        assert "13812345678" not in redacted
        assert "test@example.com" not in redacted
        assert len(mapping) > 0
    
    def test_analyze_task_type_analysis(self):
        task = "请分析这份报告的主要观点"
        task_type = self.splitter.analyze_task_type(task)
        assert task_type == TaskType.ANALYSIS
    
    def test_analyze_task_type_summarization(self):
        task = "请总结这篇文章的核心内容"
        task_type = self.splitter.analyze_task_type(task)
        assert task_type == TaskType.SUMMARIZATION
    
    def test_split_single_strategy(self):
        task = "这是一个简短的任务"
        result = self.splitter.split(task, strategy="single")
        assert len(result.subtasks) == 1
        assert result.split_strategy == "single"
    
    def test_split_section_strategy(self):
        task = "第一段内容。\n\n第二段内容。\n\n第三段内容。"
        result = self.splitter.split(task, strategy="section")
        assert len(result.subtasks) >= 1


class TestPrivacyHandler:
    
    def setup_method(self):
        self.handler = PrivacyHandler()
    
    def test_detect_phone(self):
        text = "联系电话：13812345678"
        detected = self.handler.detect(text)
        assert len(detected) > 0
        assert detected[0].info_type == "phone"
    
    def test_detect_email(self):
        text = "Email: user@example.com"
        detected = self.handler.detect(text)
        assert any(d.info_type == "email" for d in detected)
    
    def test_redact_and_restore(self):
        text = "张三的电话是13812345678"
        redacted, mapping = self.handler.redact(text)
        
        assert "13812345678" not in redacted
        assert len(mapping) > 0
        
        restored = self.handler.restore(redacted, mapping)
        assert "13812345678" in restored
    
    def test_generate_report(self):
        text = "联系方式：13812345678，邮箱：test@example.com"
        report = self.handler.generate_report(text)
        
        assert report.total_items_detected >= 2
        # Updated to use overall_risk_level instead of risk_level
        assert report.overall_risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        # Also check risk_level value
        assert report.overall_risk_level.value in ["low", "medium", "high", "critical"]
    
    def test_custom_pattern(self):
        handler = PrivacyHandler()
        handler.add_custom_pattern("custom_id", r"CUSTOM-\d{4}")
        
        text = "ID: CUSTOM-1234"
        detected = handler.detect(text)
        assert any(d.info_type == "custom_id" for d in detected)


class TestResultAggregator:
    
    def setup_method(self):
        # Use lower threshold for tests to avoid quality filtering issues
        self.aggregator = ResultAggregator(min_quality_threshold=0.1)
    
    def test_aggregate_single_result(self):
        results = [
            SubTaskResult(
                subtask_id="task_1",
                provider="openai",
                result="这是结果，包含足够长的内容来通过质量评估。我们需要更多的文字来确保质量评分达到要求。",
                success=True,
            )
        ]
        
        aggregated = self.aggregator.aggregate(results)
        assert "这是结果" in aggregated.final_result
        assert len(aggregated.providers_used) == 1
    
    def test_aggregate_parallel_merge(self):
        results = [
            SubTaskResult(
                subtask_id="task_1",
                provider="openai",
                result="第一个结果，包含详细的信息和分析内容。这是一个高质量的输出，包含多个句子。",
                success=True,
            ),
            SubTaskResult(
                subtask_id="task_2",
                provider="anthropic",
                result="第二个结果，同样包含丰富的内容和详细的说明。这是另一个高质量的输出示例。",
                success=True,
            ),
        ]
        
        aggregated = self.aggregator.aggregate(
            results,
            strategy=AggregationStrategy.PARALLEL_MERGE,
        )
        
        assert len(aggregated.providers_used) == 2
        assert len(aggregated.final_result) > 0
    
    def test_aggregate_with_failures(self):
        results = [
            SubTaskResult(
                subtask_id="task_1",
                provider="openai",
                result="成功结果，这是一个成功的任务执行结果，包含足够的内容来通过质量评估。",
                success=True,
            ),
            SubTaskResult(
                subtask_id="task_2",
                provider="anthropic",
                result="",
                success=False,
                error="API Error",
            ),
        ]
        
        aggregated = self.aggregator.aggregate(results)
        assert "成功结果" in aggregated.final_result
        assert len(aggregated.subtask_results) == 2
    
    def test_restore_sensitive_info(self):
        result = "用户 [REDACTED_PHONE_0] 的信息"
        mapping = {"[REDACTED_PHONE_0]": "13812345678"}
        
        restored = self.aggregator.restore_sensitive_info(result, mapping)
        assert "13812345678" in restored
        assert "[REDACTED_PHONE_0]" not in restored
    
    def test_aggregate_empty_results(self):
        aggregated = self.aggregator.aggregate([])
        assert aggregated.final_result == ""
        assert len(aggregated.providers_used) == 0


class TestIntegration:
    
    def test_full_pipeline(self):
        splitter = TaskSplitter()
        privacy = PrivacyHandler()
        aggregator = ResultAggregator(min_quality_threshold=0.1)
        
        task = "分析张三（电话13812345678）的反馈信息"
        
        redacted, mapping = privacy.redact(task)
        assert "13812345678" not in redacted
        
        split_result = splitter.split(redacted, strategy="single")
        assert len(split_result.subtasks) == 1
        
        mock_result = SubTaskResult(
            subtask_id="subtask_001",
            provider="test",
            result="分析完成，用户反馈积极。这是一个详细的分析结果，包含多个方面的评估和建议。",
            success=True,
        )
        
        aggregated = aggregator.aggregate([mock_result])
        restored = aggregator.restore_sensitive_info(
            aggregated.final_result,
            mapping,
        )
        
        assert len(aggregated.final_result) > 0
        assert len(restored) > 0
    
    def test_privacy_redaction_flow(self):
        privacy = PrivacyHandler()
        
        text = "客户张三的电话是13812345678，邮箱zhangsan@test.com"
        redacted, mapping = privacy.redact(text)
        
        assert "13812345678" not in redacted
        assert "zhangsan@test.com" not in redacted
        assert len(mapping) >= 2
        
        restored = privacy.restore(redacted, mapping)
        assert "13812345678" in restored
        assert "zhangsan@test.com" in restored
