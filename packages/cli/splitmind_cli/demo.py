"""
SplitMind Demo - Zero-config privacy demonstration.

This module provides a demo mode that works without any API keys,
showing users the privacy protection capabilities immediately.
"""

from typing import Dict, List
from dataclasses import dataclass
from splitmind_core.privacy import PrivacyHandler, PrivacyReport


@dataclass
class DemoResult:
    original_text: str
    redacted_text: str
    risk_level: str
    risk_score: int
    detected_items: Dict[str, List[str]]
    protection_rate: float
    
    def to_dict(self) -> Dict:
        return {
            "original_text": self.original_text,
            "redacted_text": self.redacted_text,
            "risk_level": self.risk_level,
            "risk_score": self.risk_score,
            "detected_items": self.detected_items,
            "protection_rate": self.protection_rate,
        }


class PrivacyDemo:
    """
    Demo mode for SplitMind - no API keys required!
    
    This demonstrates the privacy protection features
    without needing to connect to any AI providers.
    """
    
    def __init__(self):
        self.privacy_handler = PrivacyHandler()
        
        self.risk_weights = {
            "phone": 20,
            "email": 15,
            "id_card_cn": 30,
            "passport": 30,
            "bank_card": 25,
            "credit_card": 25,
            "amount": 5,
            "ipv4": 10,
            "url": 5,
            "date": 2,
            "time": 2,
        }
    
    def analyze(self, text: str) -> DemoResult:
        report = self.privacy_handler.generate_report(text)
        risk_score = self._calculate_risk_score(report)
        protection_rate = self._calculate_protection_rate(text, report.redacted_text)
        detected_items = self._extract_detected_items(report)
        
        return DemoResult(
            original_text=text,
            redacted_text=report.redacted_text,
            risk_level=report.risk_level,
            risk_score=risk_score,
            detected_items=detected_items,
            protection_rate=protection_rate,
        )
    
    def _calculate_risk_score(self, report: PrivacyReport) -> int:
        score = 0
        for info_type, count in report.items_by_type.items():
            weight = self.risk_weights.get(info_type, 10)
            score += weight * count
        return min(score, 100)
    
    def _calculate_protection_rate(self, original: str, redacted: str) -> float:
        original_len = len(original)
        if original_len == 0:
            return 0.0
        
        import re
        placeholders = len(re.findall(r'\[REDACTED_\w+_\d+\]', redacted))
        
        if placeholders > 0:
            return min(95.0, 50.0 + placeholders * 10.0)
        
        return 0.0
    
    def _extract_detected_items(self, report: PrivacyReport) -> Dict[str, List[str]]:
        items: Dict[str, List[str]] = {}
        for item in report.sensitive_items:
            if item.info_type not in items:
                items[item.info_type] = []
            items[item.info_type].append(item.original_value)
        return items
    
    def generate_share_card(self, result: DemoResult) -> str:
        level_markers = {
            "low": "[LOW]",
            "medium": "[MEDIUM]",
            "high": "[HIGH]",
            "critical": "[CRITICAL]",
        }
        
        marker = level_markers.get(result.risk_level, "[UNKNOWN]")
        
        card = f"""
Privacy Risk Report {marker}
━━━━━━━━━━━━━━━━━━━━━━
Risk Level: {result.risk_level.upper()}
Risk Score: {result.risk_score}/100
Protection: {result.protection_rate:.0f}%

Detected:
"""
        for info_type, items in result.detected_items.items():
            card += f"  * {info_type}: {len(items)} item(s)\n"
        
        card += """
Protected by SplitMind
Analyze your text: [link]
"""
        return card


def quick_demo(text: str = None) -> DemoResult:
    if text is None:
        text = """
        客户信息：
        姓名：张三
        电话：13812345678
        邮箱：zhangsan@example.com
        身份证号：320123199001011234
        地址：北京市朝阳区xxx街道123号
        """
    
    demo = PrivacyDemo()
    return demo.analyze(text)


if __name__ == "__main__":
    result = quick_demo()
    
    print("=" * 60)
    print("SplitMind Privacy Demo")
    print("=" * 60)
    print(f"\nOriginal text:")
    print(result.original_text)
    print(f"\nRedacted text:")
    print(result.redacted_text)
    print(f"\nRisk Level: {result.risk_level}")
    print(f"Risk Score: {result.risk_score}/100")
    print(f"Protection Rate: {result.protection_rate:.0f}%")
    print("\nDetected items:")
    for info_type, items in result.detected_items.items():
        print(f"  - {info_type}: {items}")
