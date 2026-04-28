# utils/validation_types.py

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class SeverityLevel(Enum):
    """Severity levels for validation messages"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationMessage:
    """Single validation message with severity level"""
    message: str
    severity: SeverityLevel
    field: Optional[str] = None
    value: Optional[Any] = None

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "message": self.message,
            "severity": self.severity.value,
            "field": self.field,
            "value": self.value
        }


@dataclass
class ValidationResult:
    """
    Tracks validation success/failure with detailed reporting.
    
    Features:
    - Collects multiple errors and warnings
    - Distinguishes between critical errors and warnings
    - Provides detailed reporting
    - Tracks validation context
    """
    is_valid: bool = True
    errors: List[ValidationMessage] = field(default_factory=list)
    warnings: List[ValidationMessage] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    def add_error(self, message: str, field: str = None, value: Any = None):
        """Add an error message"""
        self.errors.append(ValidationMessage(
            message=message,
            severity=SeverityLevel.ERROR,
            field=field,
            value=value
        ))
        self.is_valid = False

    def add_warning(self, message: str, field: str = None, value: Any = None):
        """Add a warning message"""
        self.warnings.append(ValidationMessage(
            message=message,
            severity=SeverityLevel.WARNING,
            field=field,
            value=value
        ))

    def add_info(self, message: str, field: str = None, value: Any = None):
        """Add an info message"""
        self.warnings.append(ValidationMessage(
            message=message,
            severity=SeverityLevel.INFO,
            field=field,
            value=value
        ))

    def set_context(self, key: str, value: Any):
        """Set context information"""
        self.context[key] = value

    def has_errors(self) -> bool:
        """Check if validation has errors"""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if validation has warnings"""
        return len(self.warnings) > 0

    def get_error_count(self) -> int:
        """Get count of errors"""
        return len(self.errors)

    def get_warning_count(self) -> int:
        """Get count of warnings"""
        return len(self.warnings)

    def get_error_messages(self) -> List[str]:
        """Get list of error messages"""
        return [msg.message for msg in self.errors]

    def get_warning_messages(self) -> List[str]:
        """Get list of warning messages"""
        return [msg.message for msg in self.warnings]

    def get_summary(self) -> str:
        """Get summary string"""
        error_count = self.get_error_count()
        warning_count = self.get_warning_count()
        
        summary = f"Validation {'PASSED' if self.is_valid else 'FAILED'}"
        
        if error_count > 0:
            summary += f" - {error_count} error(s)"
        if warning_count > 0:
            summary += f" - {warning_count} warning(s)"
        
        return summary

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "is_valid": self.is_valid,
            "errors": [msg.to_dict() for msg in self.errors],
            "warnings": [msg.to_dict() for msg in self.warnings],
            "context": self.context,
            "summary": self.get_summary()
        }

    def __str__(self):
        """String representation"""
        parts = [self.get_summary()]
        
        for error in self.errors:
            parts.append(f"  ✗ {error.message}")
        
        for warning in self.warnings:
            parts.append(f"  ⚠ {warning.message}")
        
        return "\n".join(parts)
