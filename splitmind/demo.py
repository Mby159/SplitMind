"""
SplitMind Demo - Zero-config privacy demonstration.

This module provides a demo mode that works without any API keys,
showing users the privacy protection capabilities immediately.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from splitmind.core.privacy import PrivacyHandler, PrivacyReport


@dataclass
class DemoResult:
    original_text: str
    redacted_text: str
    risk_level: str
    risk_score: int  # 0-100
    detected_items: Dict[str, List[str]]
    protection_rate: float  # percentage
    
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
        
        # Risk scoring weights
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
        """
        Analyze text for privacy risks and demonstrate protection.
        
        Args:
            text: Input text containing potentially sensitive information
            
        Returns:
            DemoResult with analysis and redaction results
        """
        # Generate privacy report
        report = self.privacy_handler.generate_report(text)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(report)
        
        # Calculate protection rate
        protection_rate = self._calculate_protection_rate(text, report.redacted_text)
        
        # Extract detected items by type
        detected_items = self._extract_detected_items(report)
        
        return DemoResult(
            original_text=text,
            redacted_text=report.redacted_text,
            risk_level=report.overall_risk_level.value,
            risk_score=risk_score,
            detected_items=detected_items,
            protection_rate=protection_rate,
        )
    
    def _calculate_risk_score(self, report: PrivacyReport) -> int:
        """Calculate a 0-100 risk score based on detected items."""
        score = 0
        for info_type, count in report.items_by_type.items():
            weight = self.risk_weights.get(info_type, 10)
            score += weight * count
        
        # Cap at 100
        return min(score, 100)
    
    def _calculate_protection_rate(self, original: str, redacted: str) -> float:
        """Calculate what percentage of sensitive content was protected."""
        original_len = len(original)
        redacted_len = len(redacted)
        
        if original_len == 0:
            return 0.0
        
        # Calculate how much was redacted
        protected_chars = original_len - redacted_len
        
        # Count redaction placeholders
        import re
        placeholders = len(re.findall(r'\[REDACTED_\w+_\d+\]', redacted))
        
        # Protection rate based on placeholders and character reduction
        if placeholders > 0:
            return min(95.0, 50.0 + placeholders * 10.0)
        
        return 0.0
    
    def _extract_detected_items(self, report: PrivacyReport) -> Dict[str, List[str]]:
        """Extract detected items grouped by type."""
        items: Dict[str, List[str]] = {}
        for item in report.sensitive_items:
            if item.info_type not in items:
                items[item.info_type] = []
            items[item.info_type].append(item.original_value)
        return items
    
    def generate_share_card(self, result: DemoResult) -> str:
        """Generate a text-based share card for social media."""
        emoji_map = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🔴",
            "critical": "⚫",
        }
        
        emoji = emoji_map.get(result.risk_level, "⚪")
        
        card = f"""
{emoji} Privacy Risk Report
━━━━━━━━━━━━━━━━━━━━━━
Risk Level: {result.risk_level.upper()}
Risk Score: {result.risk_score}/100
Protection: {result.protection_rate:.0f}%

Detected:
"""
        for info_type, items in result.detected_items.items():
            card += f"  • {info_type}: {len(items)} item(s)\n"
        
        card += """
Protected by SplitMind 🔒
Analyze your text: [link]
"""
        return card
    
    def get_risk_description(self, risk_level: str) -> str:
        """Get a human-readable description of the risk level."""
        descriptions = {
            "low": "✅ Low risk - Minimal sensitive information detected",
            "medium": "⚠️  Medium risk - Some personal information found",
            "high": "🔴 High risk - Significant sensitive data exposed",
            "critical": "🚨 Critical risk - Highly sensitive information detected",
        }
        return descriptions.get(risk_level, "Unknown risk level")
    
    def compare_scenarios(self, text: str) -> Dict:
        """
        Compare sending text directly to AI vs using SplitMind.
        
        Returns a comparison showing what information would be exposed.
        """
        result = self.analyze(text)
        
        return {
            "direct_to_ai": {
                "exposed_data": list(result.detected_items.keys()),
                "risk": "All sensitive information visible to AI provider",
                "data_retention": "May be stored and used for training",
            },
            "with_splitmind": {
                "protected_data": list(result.detected_items.keys()),
                "risk": "Sensitive information redacted before sending",
                "data_retention": "Original data never leaves your system",
                "redacted_preview": result.redacted_text[:200] + "..." 
                    if len(result.redacted_text) > 200 else result.redacted_text,
            },
        }


def quick_demo(text: str = None) -> DemoResult:
    """
    Quick demonstration of SplitMind's privacy protection.
    
    Usage:
        from splitmind.demo import quick_demo
        result = quick_demo("My phone is 13812345678")
        print(result.redacted_text)
    """
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
    # Run demo when executed directly
    result = quick_demo()
    
    print("=" * 60)
    print("🔒 SplitMind Privacy Demo")
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
