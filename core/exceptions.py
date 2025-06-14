# core/exceptions.py
"""
Centralized exception management system with comprehensive error handling,
circuit breaker patterns, and structured error responses.
"""

import asyncio
import logging
import time
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, List, Optional, Callable, Union
from functools import wraps

logger = logging.getLogger(__name__)


class ErrorSeverity(str, Enum):
    """Error severity levels"""
    LOW = "low"           # Warning-level, system continues
    MEDIUM = "medium"     # Error-level, affects single operation
    HIGH = "high"         # Critical-level, affects workflow
    CRITICAL = "critical" # System-level, requires immediate attention


class ErrorCategory(str, Enum):
    """Error categorization for better handling"""
    VALIDATION = "validation"         # Input validation errors
    AUTHENTICATION = "authentication" # Auth/permission errors
    EXTERNAL_API = "external_api"     # Third-party service errors
    BUSINESS_LOGIC = "business_logic" # Domain rule violations
    SYSTEM = "system"                 # Infrastructure errors
    NETWORK = "network"               # Connectivity issues
    RATE_LIMIT = "rate_limit"         # Rate limiting errors
    TIMEOUT = "timeout"               # Operation timeout errors


class RetryStrategy(str, Enum):
    """Retry strategy types"""
    NO_RETRY = "no_retry"           # Don't retry
    IMMEDIATE = "immediate"         # Retry immediately
    LINEAR_BACKOFF = "linear"       # Linear delay increase
    EXPONENTIAL_BACKOFF = "exponential"  # Exponential delay increase
    CUSTOM = "custom"               # Custom retry logic


@dataclass
class ErrorContext:
    """Context information for errors"""
    operation: str
    component: str
    user_id: Optional[str] = None
    campaign_id: Optional[str] = None
    creator_id: Optional[str] = None
    request_id: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    strategy: RetryStrategy = RetryStrategy.NO_RETRY
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_multiplier: float = 2.0
    jitter: bool = True


# ============================================================================
# BASE EXCEPTION HIERARCHY
# ============================================================================

class InfluencerFlowException(Exception):
    """
    Base exception for all InfluencerFlow platform errors.
    Provides structured error information and handling capabilities.
    """
    
    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        error_code: Optional[str] = None,
        context: Optional[ErrorContext] = None,
        retry_config: Optional[RetryConfig] = None,
        user_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.category = category
        self.error_code = error_code or self._generate_error_code()
        self.context = context or ErrorContext(operation="unknown", component="unknown")
        self.retry_config = retry_config or RetryConfig()
        self.user_message = user_message or self._generate_user_message()
        self.details = details or {}
        self.timestamp = datetime.now()
        self.traceback = traceback.format_exc()
    
    def _generate_error_code(self) -> str:
        """Generate a unique error code"""
        class_name = self.__class__.__name__
        timestamp = int(time.time() * 1000)
        return f"{class_name.upper()}_{timestamp}"
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly error message"""
        return "An error occurred while processing your request. Please try again."
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/API responses"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "user_message": self.user_message,
            "severity": self.severity.value,
            "category": self.category.value,
            "timestamp": self.timestamp.isoformat(),
            "context": {
                "operation": self.context.operation,
                "component": self.context.component,
                "campaign_id": self.context.campaign_id,
                "creator_id": self.context.creator_id,
                "request_id": self.context.request_id,
                **self.context.additional_data
            },
            "details": self.details,
            "retry_recommended": self.retry_config.strategy != RetryStrategy.NO_RETRY
        }
    
    def should_retry(self) -> bool:
        """Check if this error should be retried"""
        return self.retry_config.strategy != RetryStrategy.NO_RETRY


# ============================================================================
# SPECIFIC EXCEPTION TYPES
# ============================================================================

class ValidationError(InfluencerFlowException):
    """Data validation errors"""
    
    def __init__(
        self, 
        message: str, 
        field_errors: Optional[Dict[str, List[str]]] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            **kwargs
        )
        self.field_errors = field_errors or {}
        self.details["field_errors"] = self.field_errors
    
    def _generate_user_message(self) -> str:
        if self.field_errors:
            return "Please check the following fields: " + ", ".join(self.field_errors.keys())
        return "Please check your input and try again."


class AuthenticationError(InfluencerFlowException):
    """Authentication and authorization errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.AUTHENTICATION,
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
        return "Authentication failed. Please check your credentials."


class ExternalAPIError(InfluencerFlowException):
    """External API service errors"""
    
    def __init__(
        self, 
        message: str, 
        service_name: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        # Determine retry strategy based on status code
        retry_config = self._determine_retry_strategy(status_code)
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.EXTERNAL_API,
            retry_config=retry_config,
            **kwargs
        )
        self.service_name = service_name
        self.status_code = status_code
        self.response_data = response_data or {}
        
        self.details.update({
            "service_name": service_name,
            "status_code": status_code,
            "response_data": response_data
        })
    
    def _determine_retry_strategy(self, status_code: Optional[int]) -> RetryConfig:
        """Determine retry strategy based on HTTP status code"""
        if not status_code:
            return RetryConfig(strategy=RetryStrategy.EXPONENTIAL_BACKOFF)
        
        # 5xx errors - retry with exponential backoff
        if 500 <= status_code < 600:
            return RetryConfig(
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
                max_attempts=3,
                base_delay=2.0
            )
        
        # 429 - rate limiting, retry with longer delay
        if status_code == 429:
            return RetryConfig(
                strategy=RetryStrategy.LINEAR_BACKOFF,
                max_attempts=5,
                base_delay=60.0
            )
        
        # 4xx errors (except 429) - don't retry
        if 400 <= status_code < 500:
            return RetryConfig(strategy=RetryStrategy.NO_RETRY)
        
        # Default - exponential backoff
        return RetryConfig(strategy=RetryStrategy.EXPONENTIAL_BACKOFF)
    
    def _generate_user_message(self) -> str:
        return f"Unable to connect to {self.service_name}. Please try again later."


class ElevenLabsAPIError(ExternalAPIError):
    """Specific ElevenLabs API errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            service_name="ElevenLabs",
            **kwargs
        )


class GroqAPIError(ExternalAPIError):
    """Specific Groq API errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            service_name="Groq",
            **kwargs
        )


class BusinessLogicError(InfluencerFlowException):
    """Business rule violations"""
    
    def __init__(self, message: str, rule_violated: str, **kwargs):
        super().__init__(
            message=message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            **kwargs
        )
        self.rule_violated = rule_violated
        self.details["rule_violated"] = rule_violated


class CampaignValidationError(BusinessLogicError):
    """Campaign-specific validation errors"""
    
    def __init__(
        self, 
        message: str, 
        validation_errors: List[str],
        **kwargs
    ):
        super().__init__(
            message=message,
            rule_violated="campaign_validation",
            **kwargs
        )
        self.validation_errors = validation_errors
        self.details["validation_errors"] = validation_errors
    
    def _generate_user_message(self) -> str:
        return "Campaign validation failed. Please check your campaign details."


class NegotiationError(BusinessLogicError):
    """Negotiation process errors"""
    
    def __init__(
        self, 
        message: str, 
        creator_id: str,
        negotiation_stage: str,
        **kwargs
    ):
        super().__init__(
            message=message,
            rule_violated="negotiation_process",
            **kwargs
        )
        self.creator_id = creator_id
        self.negotiation_stage = negotiation_stage
        
        # Update context
        if self.context:
            self.context.creator_id = creator_id
        
        self.details.update({
            "creator_id": creator_id,
            "negotiation_stage": negotiation_stage
        })


class RateLimitError(InfluencerFlowException):
    """Rate limiting errors"""
    
    def __init__(
        self, 
        message: str, 
        service: str,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        retry_config = RetryConfig(
            strategy=RetryStrategy.LINEAR_BACKOFF,
            max_attempts=3,
            base_delay=retry_after or 60
        )
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.RATE_LIMIT,
            retry_config=retry_config,
            **kwargs
        )
        self.service = service
        self.retry_after = retry_after
        
        self.details.update({
            "service": service,
            "retry_after": retry_after
        })
    
    def _generate_user_message(self) -> str:
        if self.retry_after:
            return f"Rate limit exceeded. Please wait {self.retry_after} seconds before trying again."
        return "Rate limit exceeded. Please try again later."


class TimeoutError(InfluencerFlowException):
    """Operation timeout errors"""
    
    def __init__(
        self, 
        message: str, 
        operation: str,
        timeout_seconds: float,
        **kwargs
    ):
        retry_config = RetryConfig(
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            max_attempts=2
        )
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.TIMEOUT,
            retry_config=retry_config,
            **kwargs
        )
        self.operation = operation
        self.timeout_seconds = timeout_seconds
        
        self.details.update({
            "operation": operation,
            "timeout_seconds": timeout_seconds
        })
    
    def _generate_user_message(self) -> str:
        return f"Operation timed out. Please try again."


class NetworkError(InfluencerFlowException):
    """Network connectivity errors"""
    
    def __init__(self, message: str, **kwargs):
        retry_config = RetryConfig(
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            max_attempts=3
        )
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.NETWORK,
            retry_config=retry_config,
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
        return "Network connection error. Please check your connection and try again."


class SystemError(InfluencerFlowException):
    """System-level errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.SYSTEM,
            **kwargs
        )
    
    def _generate_user_message(self) -> str:
        return "A system error occurred. Our team has been notified."


# ============================================================================
# CIRCUIT BREAKER PATTERN
# ============================================================================

class CircuitBreakerState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"          # Failures detected, requests blocked
    HALF_OPEN = "half_open" # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    timeout_seconds: float = 60.0
    success_threshold: int = 3  # For half-open state


class CircuitBreaker:
    """Circuit breaker implementation for external services"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.last_attempt_time = 0
    
    def should_allow_request(self) -> bool:
        """Check if request should be allowed"""
        now = time.time()
        
        if self.state == CircuitBreakerState.CLOSED:
            return True
        
        elif self.state == CircuitBreakerState.OPEN:
            if now - self.last_failure_time >= self.config.timeout_seconds:
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                return True
            return False
        
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return True
        
        return False
    
    def record_success(self):
        """Record a successful operation"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
        elif self.state == CircuitBreakerState.CLOSED:
            self.failure_count = 0
    
    def record_failure(self):
        """Record a failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
        elif (self.state == CircuitBreakerState.CLOSED and 
              self.failure_count >= self.config.failure_threshold):
            self.state = CircuitBreakerState.OPEN
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time
        }


# ============================================================================
# RETRY MECHANISM
# ============================================================================

class RetryManager:
    """Manages retry logic for failed operations"""
    
    @staticmethod
    async def execute_with_retry(
        operation: Callable,
        retry_config: RetryConfig,
        context: Optional[ErrorContext] = None,
        *args,
        **kwargs
    ):
        """Execute operation with retry logic"""
        last_exception = None
        
        for attempt in range(retry_config.max_attempts):
            try:
                result = await operation(*args, **kwargs)
                logger.info(f"Operation succeeded on attempt {attempt + 1}")
                return result
                
            except InfluencerFlowException as e:
                last_exception = e
                
                # Check if we should retry this specific error
                if not e.should_retry() or attempt == retry_config.max_attempts - 1:
                    logger.error(f"Operation failed permanently: {e}")
                    raise e
                
                # Calculate delay
                delay = RetryManager._calculate_delay(retry_config, attempt)
                
                logger.warning(
                    f"Operation failed (attempt {attempt + 1}/{retry_config.max_attempts}). "
                    f"Retrying in {delay:.2f}s. Error: {e.message}"
                )
                
                await asyncio.sleep(delay)
            
            except Exception as e:
                # Wrap non-InfluencerFlow exceptions
                wrapped_exception = InfluencerFlowException(
                    message=str(e),
                    context=context,
                    retry_config=retry_config
                )
                last_exception = wrapped_exception
                
                if attempt == retry_config.max_attempts - 1:
                    raise wrapped_exception
                
                delay = RetryManager._calculate_delay(retry_config, attempt)
                logger.warning(f"Unexpected error (attempt {attempt + 1}). Retrying in {delay:.2f}s")
                await asyncio.sleep(delay)
        
        # Should not reach here, but raise last exception if we do
        if last_exception:
            raise last_exception
    
    @staticmethod
    def _calculate_delay(config: RetryConfig, attempt: int) -> float:
        """Calculate delay for retry attempt"""
        if config.strategy == RetryStrategy.NO_RETRY:
            return 0
        
        elif config.strategy == RetryStrategy.IMMEDIATE:
            return 0
        
        elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = config.base_delay * (attempt + 1)
        
        elif config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = config.base_delay * (config.backoff_multiplier ** attempt)
        
        else:
            delay = config.base_delay
        
        # Apply jitter if enabled
        if config.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)  # ±50% jitter
        
        # Respect max delay
        return min(delay, config.max_delay)


# ============================================================================
# ERROR HANDLER AND LOGGING
# ============================================================================

class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.error_counts: Dict[str, int] = {}
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_name not in self.circuit_breakers:
            config = CircuitBreakerConfig()
            self.circuit_breakers[service_name] = CircuitBreaker(service_name, config)
        
        return self.circuit_breakers[service_name]
    
    async def handle_error(
        self, 
        error: Exception, 
        context: Optional[ErrorContext] = None
    ) -> Dict[str, Any]:
        """Handle and log error, return structured response"""
        
        # Convert to InfluencerFlowException if needed
        if not isinstance(error, InfluencerFlowException):
            error = InfluencerFlowException(
                message=str(error),
                context=context,
                severity=ErrorSeverity.MEDIUM
            )
        
        # Log error
        self._log_error(error)
        
        # Track error metrics
        self._track_error_metrics(error)
        
        # Handle circuit breaker
        if error.category == ErrorCategory.EXTERNAL_API:
            service_name = error.details.get("service_name", "unknown")
            circuit_breaker = self.get_circuit_breaker(service_name)
            circuit_breaker.record_failure()
        
        # Return structured error response
        return error.to_dict()
    
    def _log_error(self, error: InfluencerFlowException):
        """Log error with appropriate level"""
        log_data = {
            "error_code": error.error_code,
            "message": error.message,
            "category": error.category.value,
            "severity": error.severity.value,
            "context": error.context.__dict__ if error.context else {},
            "details": error.details
        }
        
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical("Critical error occurred", extra=log_data)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error("High severity error", extra=log_data)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning("Medium severity error", extra=log_data)
        else:
            logger.info("Low severity error", extra=log_data)
    
    def _track_error_metrics(self, error: InfluencerFlowException):
        """Track error metrics for monitoring"""
        error_key = f"{error.category.value}:{error.__class__.__name__}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
    
    def get_error_metrics(self) -> Dict[str, Any]:
        """Get error metrics for monitoring"""
        circuit_breaker_status = {
            name: cb.get_status() 
            for name, cb in self.circuit_breakers.items()
        }
        
        return {
            "error_counts": self.error_counts,
            "circuit_breakers": circuit_breaker_status,
            "total_errors": sum(self.error_counts.values())
        }


# ============================================================================
# DECORATORS FOR AUTOMATIC ERROR HANDLING
# ============================================================================

def handle_exceptions(
    retry_config: Optional[RetryConfig] = None,
    circuit_breaker_service: Optional[str] = None,
    context_factory: Optional[Callable] = None
):
    """Decorator for automatic exception handling"""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create context
            context = None
            if context_factory:
                try:
                    context = context_factory(*args, **kwargs)
                except Exception:
                    context = ErrorContext(operation=func.__name__, component=func.__module__)
            else:
                context = ErrorContext(operation=func.__name__, component=func.__module__)
            
            # Check circuit breaker
            if circuit_breaker_service:
                error_handler = ErrorHandler()
                circuit_breaker = error_handler.get_circuit_breaker(circuit_breaker_service)
                
                if not circuit_breaker.should_allow_request():
                    raise ExternalAPIError(
                        message=f"Circuit breaker open for {circuit_breaker_service}",
                        service_name=circuit_breaker_service,
                        context=context
                    )
            
            # Execute with retry if configured
            if retry_config:
                try:
                    result = await RetryManager.execute_with_retry(
                        func, retry_config, context, *args, **kwargs
                    )
                    
                    # Record success for circuit breaker
                    if circuit_breaker_service:
                        circuit_breaker.record_success()
                    
                    return result
                    
                except InfluencerFlowException:
                    # Record failure for circuit breaker
                    if circuit_breaker_service:
                        circuit_breaker.record_failure()
                    raise
            else:
                # Execute without retry
                try:
                    result = await func(*args, **kwargs)
                    
                    # Record success for circuit breaker
                    if circuit_breaker_service:
                        circuit_breaker.record_success()
                    
                    return result
                    
                except Exception as e:
                    # Record failure for circuit breaker
                    if circuit_breaker_service:
                        circuit_breaker.record_failure()
                    
                    # Convert to InfluencerFlowException if needed
                    if not isinstance(e, InfluencerFlowException):
                        raise InfluencerFlowException(
                            message=str(e),
                            context=context
                        )
                    raise
        
        return wrapper
    return decorator


def elevenlabs_service():
    """Decorator for ElevenLabs service calls"""
    retry_config = RetryConfig(
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        max_attempts=3,
        base_delay=2.0
    )
    
    return handle_exceptions(
        retry_config=retry_config,
        circuit_breaker_service="elevenlabs"
    )


def groq_service():
    """Decorator for Groq service calls"""
    retry_config = RetryConfig(
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        max_attempts=2,
        base_delay=1.0
    )
    
    return handle_exceptions(
        retry_config=retry_config,
        circuit_breaker_service="groq"
    )


# ============================================================================
# GLOBAL ERROR HANDLER INSTANCE
# ============================================================================

# Global error handler instance
global_error_handler = ErrorHandler()


# Helper function for easy error handling
async def handle_and_log_error(error: Exception, context: Optional[ErrorContext] = None) -> Dict[str, Any]:
    """Convenience function for error handling"""
    return await global_error_handler.handle_error(error, context)


# Helper function for creating error context
def create_error_context(
    operation: str,
    component: str,
    campaign_id: Optional[str] = None,
    creator_id: Optional[str] = None,
    **additional_data
) -> ErrorContext:
    """Helper function to create error context"""
    return ErrorContext(
        operation=operation,
        component=component,
        campaign_id=campaign_id,
        creator_id=creator_id,
        additional_data=additional_data
    )