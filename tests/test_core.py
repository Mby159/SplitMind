import pytest
from splitmind.core.privacy import PrivacyHandler, RiskLevel
from splitmind.core.splitter import TaskSplitter, SubTask
from splitmind.core.aggregator import ResultAggregator, SubTaskResult, ResultQuality
from splitmind.core.local_model import LocalModelInterface
from splitmind.core.engine import SplitMindEngine, ExecutionMode, ExecutionConfig, ExecutionResult

class TestPrivacyHandler:
    """测试隐私处理器功能"""
    
    def test_detect_sensitive_info(self):
        """测试检测敏感信息"""
        privacy_handler = PrivacyHandler()
        text = "我的邮箱是 example@example.com，电话号码是 13800138000，身份证号是 110101199001011234"
        sensitive_info = privacy_handler.detect_sensitive_info(text)
        
        assert len(sensitive_info) > 0
        assert any(info['type'] == 'email' for info in sensitive_info)
        assert any(info['type'] == 'phone' for info in sensitive_info)
        assert any(info['type'] == 'id_card' for info in sensitive_info)
    
    def test_redact_sensitive_info(self):
        """测试脱敏处理"""
        privacy_handler = PrivacyHandler()
        text = "我的邮箱是 example@example.com，电话号码是 13800138000"
        redacted_text, mappings = privacy_handler.redact_sensitive_info(text)
        
        assert "[EMAIL_0]" in redacted_text
        assert "[PHONE_1]" in redacted_text
        assert "example@example.com" not in redacted_text
        assert "13800138000" not in redacted_text
        assert len(mappings) == 2
    
    def test_restore_sensitive_info(self):
        """测试还原敏感信息"""
        privacy_handler = PrivacyHandler()
        text = "我的邮箱是 example@example.com，电话号码是 13800138000"
        redacted_text, mappings = privacy_handler.redact_sensitive_info(text)
        restored_text = privacy_handler.restore_sensitive_info(redacted_text, mappings)
        
        assert restored_text == text
    
    def test_assess_risk(self):
        """测试风险评估"""
        privacy_handler = PrivacyHandler()
        
        # 低风险文本
        low_risk_text = "这是一段普通文本，没有敏感信息"
        low_risk = privacy_handler.assess_risk(low_risk_text)
        assert low_risk == RiskLevel.LOW
        
        # 中风险文本
        medium_risk_text = "我的邮箱是 example@example.com"
        medium_risk = privacy_handler.assess_risk(medium_risk_text)
        assert medium_risk in [RiskLevel.MEDIUM, RiskLevel.HIGH]
        
        # 高风险文本
        high_risk_text = "我的身份证号是 110101199001011234，银行卡号是 6222021234567890123"
        high_risk = privacy_handler.assess_risk(high_risk_text)
        assert high_risk == RiskLevel.HIGH

class TestTaskSplitter:
    """测试任务拆分器功能"""
    
    def test_split_task_single(self):
        """测试单任务拆分策略"""
        splitter = TaskSplitter()
        task = "请分析这份财务报告"
        subtasks = splitter.split_task(task, strategy="single")
        
        assert len(subtasks) == 1
        assert subtasks[0].content == task
    
    def test_split_task_section(self):
        """测试分段拆分策略"""
        splitter = TaskSplitter()
        task = "请分析这份财务报告。提取关键指标。生成摘要。"
        subtasks = splitter.split_task(task, strategy="section")
        
        assert len(subtasks) > 1
    
    def test_split_task_parallel(self):
        """测试并行拆分策略"""
        splitter = TaskSplitter()
        task = "请分析财务报告并提取关键指标"
        subtasks = splitter.split_task(task, strategy="parallel")
        
        assert len(subtasks) > 1
    
    def test_calculate_execution_order(self):
        """测试计算执行顺序"""
        splitter = TaskSplitter()
        
        # 创建具有依赖关系的子任务
        subtask1 = SubTask(task_id="1", content="任务1", dependencies=[])
        subtask2 = SubTask(task_id="2", content="任务2", dependencies=["1"])
        subtask3 = SubTask(task_id="3", content="任务3", dependencies=["2"])
        
        execution_order = splitter.calculate_execution_order([subtask1, subtask2, subtask3])
        assert execution_order == ["1", "2", "3"]

    def test_redaction_uses_privacy_handler_without_false_name_cn(self):
        """实际子任务脱敏应与 PrivacyHandler 基础类型一致，避免把提示词误判成人名。"""
        splitter = TaskSplitter()
        task = "请分析客户需求，客户邮箱是 alice@example.com，手机号是 13800138000。"
        result = splitter.split(task, strategy="single")
        subtask = result.subtasks[0]

        assert "[REDACTED_EMAIL_0]" in subtask.input_data
        assert "[REDACTED_PHONE_0]" in subtask.input_data
        assert "[REDACTED_NAME_CN_0]" not in subtask.input_data
        assert subtask.sensitive_info == {
            "[REDACTED_EMAIL_0]": "alice@example.com",
            "[REDACTED_PHONE_0]": "13800138000",
        }

    def test_redaction_placeholder_order_is_position_stable(self):
        """占位符编号应按文本出现位置稳定生成，且重复值按出现次数处理。"""
        splitter = TaskSplitter()
        text = "先联系 a@example.com，再联系 b@example.com，备用邮箱 a@example.com。"
        redacted, mapping = splitter.redact_text(text)

        assert redacted == "先联系 [REDACTED_EMAIL_0]，再联系 [REDACTED_EMAIL_1]，备用邮箱 [REDACTED_EMAIL_2]。"
        assert mapping == {
            "[REDACTED_EMAIL_0]": "a@example.com",
            "[REDACTED_EMAIL_1]": "b@example.com",
            "[REDACTED_EMAIL_2]": "a@example.com",
        }

    def test_engine_privacy_report_matches_subtask_redaction_types(self):
        """引擎隐私报告和实际子任务映射不应描述两套不同的脱敏行为。"""
        engine = SplitMindEngine(config=ExecutionConfig(execution_mode=ExecutionMode.LOCAL_ONLY))
        task = "请分析客户需求，客户邮箱是 alice@example.com，手机号是 13800138000。"
        result = engine.execute_sync(task, split_strategy="single")

        subtask = result.split_result.subtasks[0]
        assert result.privacy_report["items_by_type"] == {"email": 1, "phone": 1}
        assert set(subtask.sensitive_info.keys()) == {"[REDACTED_EMAIL_0]", "[REDACTED_PHONE_0]"}

class TestResultAggregator:
    """测试结果聚合器功能"""
    
    def test_aggregate_sequential(self):
        """测试顺序聚合策略"""
        aggregator = ResultAggregator()
        results = [
            SubTaskResult(task_id="1", content="分析显示收入增长 10%"),
            SubTaskResult(task_id="2", content="利润提升 15%"),
            SubTaskResult(task_id="3", content="建议增加市场投入")
        ]
        aggregated = aggregator.aggregate(results, strategy="sequential")
        
        assert isinstance(aggregated, str)
        assert "收入增长 10%" in aggregated
        assert "利润提升 15%" in aggregated
        assert "建议增加市场投入" in aggregated
    
    def test_assess_quality(self):
        """测试结果质量评估"""
        aggregator = ResultAggregator()
        
        # 高质量结果
        high_quality = "这是一个详细、准确的分析报告，包含了所有关键信息。"
        quality_high = aggregator.assess_quality(high_quality)
        assert quality_high in [ResultQuality.HIGH, ResultQuality.MEDIUM]
        
        # 低质量结果
        low_quality = "不知道"
        quality_low = aggregator.assess_quality(low_quality)
        assert quality_low in [ResultQuality.LOW, ResultQuality.MEDIUM]
    
    def test_detect_conflicts(self):
        """测试冲突检测"""
        aggregator = ResultAggregator()
        
        # 无冲突的结果
        results_no_conflict = [
            SubTaskResult(task_id="1", content="收入增长 10%"),
            SubTaskResult(task_id="2", content="利润提升 15%")
        ]
        conflicts_no = aggregator.detect_conflicts(results_no_conflict)
        assert len(conflicts_no) == 0
        
        # 有冲突的结果
        results_conflict = [
            SubTaskResult(task_id="1", content="收入增长 10%"),
            SubTaskResult(task_id="2", content="收入下降 5%")
        ]
        conflicts = aggregator.detect_conflicts(results_conflict)
        assert len(conflicts) > 0

class TestLocalModelInterface:
    """测试本地模型接口功能"""
    
    def test_generate(self):
        """测试文本生成"""
        local_model = LocalModelInterface(model="llama3.2:3b")
        response = local_model.generate("Hello, how are you?")
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_classify(self):
        """测试文本分类"""
        local_model = LocalModelInterface(model="llama3.2:3b")
        classification = local_model.classify("This is a test", labels=["positive", "negative", "neutral"])
        
        assert isinstance(classification, str)
        assert classification in ["positive", "negative", "neutral"]
    
    def test_merge_results(self):
        """测试结果合并"""
        local_model = LocalModelInterface(model="llama3.2:3b")
        results = ["Result 1", "Result 2", "Result 3"]
        merged = local_model.merge_results(results)
        
        assert isinstance(merged, str)
        assert len(merged) > 0

class TestEngine:
    """测试引擎功能"""
    
    def test_execute_sync_local_only(self):
        """测试本地模式处理任务"""
        engine = SplitMindEngine(config=ExecutionConfig(execution_mode=ExecutionMode.LOCAL_ONLY))
        task = "请告诉我 1 + 1 等于多少"
        result = engine.execute_sync(task)
        
        assert isinstance(result, ExecutionResult)
        assert result.success
        assert len(result.final_result) > 0
    
    def test_config_execution_mode(self):
        """测试设置执行模式"""
        # 测试 LOCAL_ONLY 模式
        engine_local = SplitMindEngine(config=ExecutionConfig(execution_mode=ExecutionMode.LOCAL_ONLY))
        assert engine_local.config.execution_mode == ExecutionMode.LOCAL_ONLY
        
        # 测试 HYBRID 模式
        engine_hybrid = SplitMindEngine(config=ExecutionConfig(execution_mode=ExecutionMode.HYBRID))
        assert engine_hybrid.config.execution_mode == ExecutionMode.HYBRID
        
        # 测试 ONLINE 模式
        engine_online = SplitMindEngine(config=ExecutionConfig(execution_mode=ExecutionMode.ONLINE))
        assert engine_online.config.execution_mode == ExecutionMode.ONLINE

if __name__ == "__main__":
    pytest.main([__file__])
