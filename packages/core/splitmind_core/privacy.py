"""
Privacy Handler - Handles sensitive data detection, redaction, and restoration.
"""

from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel
import re
import hashlib
import json


class SensitiveInfo(BaseModel):
    info_type: str
    original_value: str
    placeholder: str
    position: Tuple[int, int]
    confidence: float = 1.0


class PrivacyReport(BaseModel):
    total_items_detected: int
    items_by_type: Dict[str, int]
    redacted_text: str
    sensitive_items: List[SensitiveInfo]
    risk_level: str


class PrivacyHandler:
    """
    Privacy Handler - Detects, redacts, and restores sensitive information.
    
    Supports multiple types of sensitive data:
    - Personal names
    - Phone numbers
    - Email addresses
    - ID card numbers
    - Bank card numbers
    - Addresses
    - Company names
    - Financial amounts
    """
    
    def __init__(
        self,
        custom_patterns: Optional[Dict[str, str]] = None,
        placeholder_format: str = "[REDACTED_{type}_{id}]",
        enable_hash_placeholder: bool = False,
    ):
        self.placeholder_format = placeholder_format
        self.enable_hash_placeholder = enable_hash_placeholder
        
        self._patterns = self._init_patterns()
        if custom_patterns:
            for name, pattern in custom_patterns.items():
                self._patterns[name] = re.compile(pattern, re.IGNORECASE)
        
        self._redaction_map: Dict[str, str] = {}
        self._counter: Dict[str, int] = {}
    
    def _init_patterns(self) -> Dict[str, re.Pattern]:
        return {
            "phone": re.compile(
                r'(?<!\d)(1[3-9]\d{9})(?!\d)|'
                r'(?<!\d)(\d{3,4}[-\s]?\d{7,8})(?!\d)'
            ),
            "email": re.compile(
                r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
            ),
            "id_card_cn": re.compile(
                r'(?<![0-9Xx])\d{17}[\dXx](?![0-9Xx])'
            ),
            "passport": re.compile(
                r'(?<![A-Z0-9])[EG]\d{8}(?![A-Z0-9])|'
                r'(?<![A-Z0-9])[A-Z]{1,2}\d{6,9}(?![A-Z0-9])'
            ),
            "bank_card": re.compile(
                r'(?<![0-9])\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}(?![0-9])'
            ),
            "amount": re.compile(
                r'(?:￥|¥|\$|USD|CNY|RMB|元|美元)\s*[\d,]+(?:\.\d{2})?|'
                r'[\d,]+(?:\.\d{2})?\s*(?:元|美元|USD|CNY|RMB|￥|¥|\$)'
            ),
            "credit_card": re.compile(
                r'\b(?:4\d{12}|5[1-5]\d{14}|3[47]\d{13}|6(?:011|5\d)\d{11})\b'
            ),
            "ipv4": re.compile(
                r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
                r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
            ),
            "url": re.compile(
                r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}'
                r'\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
            ),
            "date": re.compile(
                r'\b\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?\b|'
                r'\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b'
            ),
            "time": re.compile(
                r'\b\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?\b'
            ),
        }
    
    def _generate_placeholder(self, info_type: str, value: str) -> str:
        self._counter[info_type] = self._counter.get(info_type, 0) + 1
        idx = self._counter[info_type]
        
        if self.enable_hash_placeholder:
            hash_val = hashlib.md5(value.encode()).hexdigest()[:8]
            return self.placeholder_format.format(type=info_type.upper(), id=hash_val)
        
        return self.placeholder_format.format(type=info_type.upper(), id=idx)
    
    def detect(self, text: str) -> List[SensitiveInfo]:
        detected = []
        
        for info_type, pattern in self._patterns.items():
            for match in pattern.finditer(text):
                value = match.group()
                placeholder = self._generate_placeholder(info_type, value)
                
                detected.append(SensitiveInfo(
                    info_type=info_type,
                    original_value=value,
                    placeholder=placeholder,
                    position=(match.start(), match.end()),
                ))
        
        return detected
    
    def redact(self, text: str) -> Tuple[str, Dict[str, str]]:
        self._redaction_map = {}
        self._counter = {}
        
        detected = self.detect(text)
        
        sorted_items = sorted(detected, key=lambda x: x.position[0], reverse=True)
        
        redacted_text = text
        for item in sorted_items:
            redacted_text = (
                redacted_text[:item.position[0]] + 
                item.placeholder + 
                redacted_text[item.position[1]:]
            )
            self._redaction_map[item.placeholder] = item.original_value
        
        return redacted_text, self._redaction_map
    
    def restore(self, text: str, mapping: Dict[str, str]) -> str:
        restored = text
        for placeholder, original in mapping.items():
            restored = restored.replace(placeholder, original)
        return restored
    
    def generate_report(self, text: str) -> PrivacyReport:
        detected = self.detect(text)
        redacted_text, _ = self.redact(text)
        
        items_by_type: Dict[str, int] = {}
        for item in detected:
            items_by_type[item.info_type] = items_by_type.get(item.info_type, 0) + 1
        
        total = len(detected)
        if total == 0:
            risk_level = "low"
        elif total <= 3:
            risk_level = "medium"
        elif total <= 10:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        return PrivacyReport(
            total_items_detected=total,
            items_by_type=items_by_type,
            redacted_text=redacted_text,
            sensitive_items=detected,
            risk_level=risk_level,
        )
    
    def add_custom_pattern(self, name: str, pattern: str) -> None:
        self._patterns[name] = re.compile(pattern, re.IGNORECASE)
    
    def remove_pattern(self, name: str) -> bool:
        if name in self._patterns:
            del self._patterns[name]
            return True
        return False
    
    def get_supported_types(self) -> List[str]:
        return list(self._patterns.keys())
    
    def mask_partial(self, text: str, mask_char: str = "*") -> Tuple[str, Dict[str, str]]:
        detected = self.detect(text)
        mapping = {}
        
        sorted_items = sorted(detected, key=lambda x: x.position[0], reverse=True)
        
        masked_text = text
        for item in sorted_items:
            value = item.original_value
            if len(value) <= 4:
                masked = mask_char * len(value)
            else:
                masked = value[:2] + mask_char * (len(value) - 4) + value[-2:]
            
            masked_text = (
                masked_text[:item.position[0]] + 
                masked + 
                masked_text[item.position[1]:]
            )
            mapping[mask_char * len(value) if len(value) <= 4 else masked] = value
        
        return masked_text, mapping
    
    def anonymize_names(
        self,
        text: str,
        names: Optional[List[str]] = None,
    ) -> Tuple[str, Dict[str, str]]:
        mapping = {}
        anonymized = text
        
        if names:
            for idx, name in enumerate(names):
                placeholder = f"[PERSON_{idx + 1}]"
                anonymized = anonymized.replace(name, placeholder)
                mapping[placeholder] = name
        
        return anonymized, mapping
    
    def create_data_contract(
        self,
        text: str,
        allowed_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        detected = self.detect(text)
        
        if allowed_types is None:
            allowed_types = []
        
        filtered_items = [
            item for item in detected
            if item.info_type in allowed_types
        ]
        
        blocked_items = [
            item for item in detected
            if item.info_type not in allowed_types
        ]
        
        return {
            "allowed_data": [
                {"type": item.info_type, "position": item.position}
                for item in filtered_items
            ],
            "blocked_data": [
                {"type": item.info_type, "position": item.position}
                for item in blocked_items
            ],
            "compliance": len(blocked_items) == 0,
            "total_detected": len(detected),
        }
