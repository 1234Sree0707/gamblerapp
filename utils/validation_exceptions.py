# utils/validation_exceptions.py

from enum import Enum
from typing import Optional, Any


class ValidationErrorType(Enum):
    """Categorizes all validation errors"""
    STAKE_ERROR = "stake_error"
    BET_ERROR = "bet_error"
    LIMIT_ERROR = "limit_error"
    PROBABILITY_ERROR = "probability_error"
    NUMERIC_ERROR = "numeric_error"
    RANGE_ERROR = "range_error"
    NULL_ERROR = "null_error"


class ValidationException(Exception):
    """
    Base exception for validation errors.
    
    Tracks error type, field name, and attempted value for detailed diagnostics.
    """

    def __init__(
        self,
        message: str,
        error_type: ValidationErrorType,
        field: str = None,
        value: Any = None
    ):
        """
        Initialize validation exception.
        
        Args:
            message: Human-readable error message
            error_type: ValidationErrorType enum value
            field: Name of the field that failed validation
            value: The value that failed validation
        """
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.field = field
        self.value = value

    def __str__(self):
        """Detailed string representation"""
        base_msg = f"[{self.error_type.value.upper()}] {self.message}"
        if self.field:
            base_msg += f" (field: {self.field})"
        if self.value is not None:
            base_msg += f" (value: {self.value})"
        return base_msg

    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            "error_type": self.error_type.value,
            "message": self.message,
            "field": self.field,
            "value": self.value
        }


class StakeValidationException(ValidationException):
    """Specific to stake-related errors"""

    def __init__(self, message: str, field: str = "stake", value: Any = None):
        super().__init__(
            message,
            ValidationErrorType.STAKE_ERROR,
            field=field,
            value=value
        )


class BetValidationException(ValidationException):
    """Specific to bet amount errors"""

    def __init__(self, message: str, field: str = "bet_amount", value: Any = None):
        super().__init__(
            message,
            ValidationErrorType.BET_ERROR,
            field=field,
            value=value
        )


class LimitValidationException(ValidationException):
    """Specific to limit boundary errors"""

    def __init__(self, message: str, field: str = "limit", value: Any = None):
        super().__init__(
            message,
            ValidationErrorType.LIMIT_ERROR,
            field=field,
            value=value
        )


class ProbabilityValidationException(ValidationException):
    """Specific to probability range errors"""

    def __init__(self, message: str, field: str = "probability", value: Any = None):
        super().__init__(
            message,
            ValidationErrorType.PROBABILITY_ERROR,
            field=field,
            value=value
        )


class NumericValidationException(ValidationException):
    """Specific to numeric input errors"""

    def __init__(self, message: str, field: str = "numeric_input", value: Any = None):
        super().__init__(
            message,
            ValidationErrorType.NUMERIC_ERROR,
            field=field,
            value=value
        )


class RangeValidationException(ValidationException):
    """Specific to range boundary errors"""

    def __init__(self, message: str, field: str = "range", value: Any = None):
        super().__init__(
            message,
            ValidationErrorType.RANGE_ERROR,
            field=field,
            value=value
        )


class NullValidationException(ValidationException):
    """Specific to null/empty value errors"""

    def __init__(self, message: str, field: str = "value", value: Any = None):
        super().__init__(
            message,
            ValidationErrorType.NULL_ERROR,
            field=field,
            value=value
        )
