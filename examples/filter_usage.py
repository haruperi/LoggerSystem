"""
Filter Usage Examples

This example demonstrates how to use filters to control which log records
are emitted by specific handlers. Filters provide fine-grained control over
logging beyond just level thresholds.

Key Concepts:
- Filters are callable objects: Callable[[LogRecord], bool]
- Return True to log the record, False to suppress it
- Each handler can have its own filter
- Multiple handlers can have different filters
- Filters can be combined for complex logic
"""

import sys
from io import StringIO
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mylogger import Logger
from mylogger.filter import LevelFilter, ModuleFilter


def example_1_basic_filter():
    """Example 1: Basic filter function"""
    print("=" * 60)
    print("Example 1: Basic Filter Function")
    print("=" * 60)
    
    logger = Logger()
    
    # Simple filter: only log messages containing "important"
    def important_only(record):
        return "important" in record.message.lower()
    
    logger.add(sys.stdout, level="TRACE", filter=important_only, format="{level} | {message}")
    
    logger.info("Regular message")
    logger.info("This is IMPORTANT information")
    logger.error("Normal error")
    logger.error("An important error occurred")
    
    print()


def example_2_lambda_filter():
    """Example 2: Lambda filter"""
    print("=" * 60)
    print("Example 2: Lambda Filter")
    print("=" * 60)
    
    logger = Logger()
    
    # Use lambda for simple filters
    logger.add(
        sys.stdout,
        level="TRACE",
        filter=lambda record: record.level.no >= 40,  # ERROR and above
        format="{level} | {message}"
    )
    
    logger.debug("Debug message - won't show")
    logger.info("Info message - won't show")
    logger.warning("Warning message - won't show")
    logger.error("Error message - will show")
    logger.critical("Critical message - will show")
    
    print()


def example_3_level_filter():
    """Example 3: Using LevelFilter"""
    print("=" * 60)
    print("Example 3: LevelFilter - Level Range")
    print("=" * 60)
    
    logger = Logger()
    
    # Only log INFO, SUCCESS, and WARNING (levels 20-30)
    level_filter = LevelFilter(min_level=20, max_level=30)
    
    logger.add(sys.stdout, level="TRACE", filter=level_filter, format="{level} | {message}")
    
    logger.trace("Trace - won't show")
    logger.debug("Debug - won't show")
    logger.info("Info - will show")
    logger.success("Success - will show")
    logger.warning("Warning - will show")
    logger.error("Error - won't show")
    logger.critical("Critical - won't show")
    
    print()


def example_4_module_filter_include():
    """Example 4: ModuleFilter - Include specific modules"""
    print("=" * 60)
    print("Example 4: ModuleFilter - Include Modules")
    print("=" * 60)
    
    logger = Logger()
    
    # Only log from specific modules
    module_filter = ModuleFilter(modules=["auth", "database"], exclude=False)
    
    logger.add(sys.stdout, level="INFO", filter=module_filter, format="{level} | {module} | {message}")
    
    # Note: In this example, all logs will be from the same module (filter_usage)
    # In a real application, different modules would be logging
    
    print("Simulated logs from different modules:")
    print("(In real usage, these would come from different source files)")
    print()
    print("From 'auth' module: Would be logged")
    print("From 'database' module: Would be logged")
    print("From 'api' module: Would NOT be logged")
    print("From 'utils' module: Would NOT be logged")
    
    print()


def example_5_module_filter_exclude():
    """Example 5: ModuleFilter - Exclude specific modules"""
    print("=" * 60)
    print("Example 5: ModuleFilter - Exclude Modules")
    print("=" * 60)
    
    logger = Logger()
    
    # Log everything EXCEPT specific modules
    module_filter = ModuleFilter(modules=["test", "debug_utils"], exclude=True)
    
    logger.add(sys.stdout, level="INFO", filter=module_filter, format="{level} | {module} | {message}")
    
    print("Simulated logs with exclusion filter:")
    print("(In real usage, these would come from different source files)")
    print()
    print("From 'app' module: Would be logged")
    print("From 'api' module: Would be logged")
    print("From 'test' module: Would NOT be logged (excluded)")
    print("From 'debug_utils' module: Would NOT be logged (excluded)")
    
    print()


def example_6_filter_with_extra_fields():
    """Example 6: Filter based on extra fields"""
    print("=" * 60)
    print("Example 6: Filter Based on Extra Fields")
    print("=" * 60)
    
    logger = Logger()
    
    # Filter for specific user
    def admin_only(record):
        return record.extra.get('role') == 'admin'
    
    logger.add(
        sys.stdout,
        level="INFO",
        filter=admin_only,
        format="{level} | user={extra[user]} role={extra[role]} | {message}"
    )
    
    print("Logging with different user roles:")
    logger.bind(user="john", role="admin").info("Admin action performed")
    logger.bind(user="jane", role="user").info("User action - won't show")
    logger.bind(user="alice", role="admin").warning("Admin warning")
    logger.bind(user="bob", role="guest").error("Guest error - won't show")
    
    print()


def example_7_multiple_handlers_different_filters():
    """Example 7: Multiple handlers with different filters"""
    print("=" * 60)
    print("Example 7: Multiple Handlers with Different Filters")
    print("=" * 60)
    
    logger = Logger()
    
    print("Setting up 3 handlers:")
    print("1. Console - only INFO messages")
    print("2. Error file - only ERROR and CRITICAL")
    print("3. Audit file - only messages with 'audit' keyword")
    print()
    
    # Handler 1: Console - only INFO
    info_filter = lambda r: r.level.name == "INFO"
    logger.add(sys.stdout, level="TRACE", filter=info_filter, format="[CONSOLE] {level} | {message}")
    
    # Handler 2: Error file - ERROR and CRITICAL
    error_filter = LevelFilter(min_level=40)
    error_stream = StringIO()  # Using StringIO to demonstrate
    logger.add(error_stream, level="TRACE", filter=error_filter, format="[ERROR FILE] {level} | {message}")
    
    # Handler 3: Audit file - messages containing "audit"
    audit_filter = lambda r: "audit" in r.message.lower()
    audit_stream = StringIO()
    logger.add(audit_stream, level="TRACE", filter=audit_filter, format="[AUDIT FILE] {level} | {message}")
    
    # Log various messages
    logger.info("Regular info message")
    logger.info("User login - audit trail")
    logger.warning("Warning message")
    logger.error("Error occurred")
    logger.error("Critical audit failure")
    logger.critical("System failure")
    
    # Show what went to each handler
    print("\n--- Error file contents ---")
    print(error_stream.getvalue())
    
    print("--- Audit file contents ---")
    print(audit_stream.getvalue())
    
    print()


def example_8_custom_filter_class():
    """Example 8: Custom filter class"""
    print("=" * 60)
    print("Example 8: Custom Filter Class")
    print("=" * 60)
    
    class KeywordFilter:
        """Filter that checks if message contains any of the keywords"""
        
        def __init__(self, keywords, case_sensitive=False):
            self.keywords = keywords
            self.case_sensitive = case_sensitive
        
        def __call__(self, record):
            message = record.message if self.case_sensitive else record.message.lower()
            keywords = self.keywords if self.case_sensitive else [k.lower() for k in self.keywords]
            return any(kw in message for kw in keywords)
    
    logger = Logger()
    
    # Filter for messages containing security-related keywords
    security_filter = KeywordFilter(
        keywords=["security", "authentication", "authorization", "breach"],
        case_sensitive=False
    )
    
    logger.add(sys.stdout, level="INFO", filter=security_filter, format="{level} | {message}")
    
    logger.info("Regular application message - won't show")
    logger.info("User authentication successful")
    logger.warning("Potential security breach detected")
    logger.error("Database connection failed - won't show")
    logger.error("Authorization failed for user")
    
    print()


def example_9_combining_filters_and():
    """Example 9: Combining filters with AND logic"""
    print("=" * 60)
    print("Example 9: Combining Filters (AND Logic)")
    print("=" * 60)
    
    class AndFilter:
        """Combine multiple filters with AND logic (all must pass)"""
        
        def __init__(self, *filters):
            self.filters = filters
        
        def __call__(self, record):
            return all(f(record) for f in self.filters)
    
    logger = Logger()
    
    # Combine: ERROR or above AND contains "critical"
    level_filter = LevelFilter(min_level=40)  # ERROR and above
    keyword_filter = lambda r: "critical" in r.message.lower()
    
    combined = AndFilter(level_filter, keyword_filter)
    
    logger.add(sys.stdout, level="TRACE", filter=combined, format="{level} | {message}")
    
    logger.info("Critical info - won't show (level too low)")
    logger.error("Regular error - won't show (no 'critical' keyword)")
    logger.error("Critical error detected - will show")
    logger.critical("System critical failure - will show")
    
    print()


def example_10_combining_filters_or():
    """Example 10: Combining filters with OR logic"""
    print("=" * 60)
    print("Example 10: Combining Filters (OR Logic)")
    print("=" * 60)
    
    class OrFilter:
        """Combine multiple filters with OR logic (any can pass)"""
        
        def __init__(self, *filters):
            self.filters = filters
        
        def __call__(self, record):
            return any(f(record) for f in self.filters)
    
    logger = Logger()
    
    # Combine: ERROR or above OR contains "urgent"
    level_filter = LevelFilter(min_level=40)  # ERROR and above
    keyword_filter = lambda r: "urgent" in r.message.lower()
    
    combined = OrFilter(level_filter, keyword_filter)
    
    logger.add(sys.stdout, level="TRACE", filter=combined, format="{level} | {message}")
    
    logger.info("Regular info - won't show")
    logger.info("Urgent info - will show (has keyword)")
    logger.warning("Urgent warning - will show (has keyword)")
    logger.error("Regular error - will show (ERROR level)")
    logger.critical("System failure - will show (CRITICAL level)")
    
    print()


def example_11_rate_limiting_filter():
    """Example 11: Rate limiting filter"""
    print("=" * 60)
    print("Example 11: Rate Limiting Filter")
    print("=" * 60)
    
    class RateLimitFilter:
        """Filter that only allows every Nth message"""
        
        def __init__(self, n):
            self.n = n
            self.count = 0
        
        def __call__(self, record):
            self.count += 1
            return self.count % self.n == 0
    
    logger = Logger()
    
    # Only log every 3rd message
    rate_limiter = RateLimitFilter(n=3)
    
    logger.add(sys.stdout, level="INFO", filter=rate_limiter, format="{level} | Message #{message}")
    
    print("Logging 10 messages, but only every 3rd will appear:")
    for i in range(1, 11):
        logger.info(str(i))
    
    print()


def example_12_time_based_filter():
    """Example 12: Time-based filter"""
    print("=" * 60)
    print("Example 12: Time-Based Filter")
    print("=" * 60)
    
    from datetime import datetime
    
    class BusinessHoursFilter:
        """Filter that only logs during business hours"""
        
        def __init__(self, start_hour=9, end_hour=17):
            self.start_hour = start_hour
            self.end_hour = end_hour
        
        def __call__(self, record):
            hour = record.time.hour
            return self.start_hour <= hour < self.end_hour
    
    logger = Logger()
    
    # Only log during business hours (9 AM - 5 PM)
    business_hours = BusinessHoursFilter(start_hour=9, end_hour=17)
    
    logger.add(sys.stdout, level="INFO", filter=business_hours, format="{time:HH:mm} | {level} | {message}")
    
    current_hour = datetime.now().hour
    if 9 <= current_hour < 17:
        print(f"Current time is during business hours ({current_hour}:00)")
        logger.info("This message appears during business hours")
    else:
        print(f"Current time is outside business hours ({current_hour}:00)")
        logger.info("This message won't appear outside business hours")
    
    print()


def example_13_complex_filter_combination():
    """Example 13: Complex filter combination"""
    print("=" * 60)
    print("Example 13: Complex Filter Combination")
    print("=" * 60)
    
    class AndFilter:
        def __init__(self, *filters):
            self.filters = filters
        def __call__(self, record):
            return all(f(record) for f in self.filters)
    
    class OrFilter:
        def __init__(self, *filters):
            self.filters = filters
        def __call__(self, record):
            return any(f(record) for f in self.filters)
    
    logger = Logger()
    
    # Complex filter: (ERROR or CRITICAL) AND (contains "database" or "connection")
    high_severity = OrFilter(
        lambda r: r.level.name == "ERROR",
        lambda r: r.level.name == "CRITICAL"
    )
    
    database_related = OrFilter(
        lambda r: "database" in r.message.lower(),
        lambda r: "connection" in r.message.lower()
    )
    
    complex_filter = AndFilter(high_severity, database_related)
    
    logger.add(sys.stdout, level="TRACE", filter_func=complex_filter, format="{level} | {message}")
    
    print("Filter: (ERROR or CRITICAL) AND (contains 'database' or 'connection')")
    print()
    
    logger.info("Database query successful - won't show (not ERROR/CRITICAL)")
    logger.warning("Connection timeout - won't show (not ERROR/CRITICAL)")
    logger.error("Database connection failed - will show")
    logger.error("File not found - won't show (not database/connection)")
    logger.critical("Database server crashed - will show")
    
    print()


def example_14_performance_filter():
    """Example 14: Performance monitoring filter"""
    print("=" * 60)
    print("Example 14: Performance Monitoring Filter")
    print("=" * 60)
    
    class PerformanceFilter:
        """Filter that only logs slow operations"""
        
        def __init__(self, threshold_ms=100):
            self.threshold_ms = threshold_ms
        
        def __call__(self, record):
            # Check if record has duration in extra fields
            duration = record.extra.get('duration_ms', 0)
            return duration >= self.threshold_ms
    
    logger = Logger()
    
    # Only log operations that take more than 100ms
    slow_ops_filter = PerformanceFilter(threshold_ms=100)
    
    logger.add(
        sys.stdout,
        level="INFO",
        filter=slow_ops_filter,
        format="{level} | {message} ({extra[duration_ms]}ms)"
    )
    
    print("Only logging slow operations (>= 100ms):")
    logger.bind(duration_ms=50).info("Quick operation - won't show")
    logger.bind(duration_ms=150).info("Slow database query")
    logger.bind(duration_ms=80).info("Fast API call - won't show")
    logger.bind(duration_ms=250).warning("Very slow external service")
    
    print()


def example_15_environment_filter():
    """Example 15: Environment-based filter"""
    print("=" * 60)
    print("Example 15: Environment-Based Filter")
    print("=" * 60)
    
    import os
    
    class EnvironmentFilter:
        """Filter based on environment variable"""
        
        def __init__(self, env_var="LOG_LEVEL", allowed_levels=None):
            self.env_var = env_var
            self.allowed_levels = allowed_levels or ["ERROR", "CRITICAL"]
            self.is_production = os.getenv("ENVIRONMENT", "development") == "production"
        
        def __call__(self, record):
            if self.is_production:
                # In production, only log specified levels
                return record.level.name in self.allowed_levels
            else:
                # In development, log everything
                return True
    
    logger = Logger()
    
    # Set environment (simulated)
    os.environ["ENVIRONMENT"] = "production"
    
    env_filter = EnvironmentFilter(allowed_levels=["ERROR", "CRITICAL"])
    
    logger.add(sys.stdout, level="TRACE", filter=env_filter, format="{level} | {message}")
    
    print("Environment: production (only ERROR and CRITICAL)")
    logger.debug("Debug message - won't show in production")
    logger.info("Info message - won't show in production")
    logger.error("Error message - will show in production")
    logger.critical("Critical message - will show in production")
    
    print()


def example_16_sampling_filter():
    """Example 16: Sampling filter for high-volume logs"""
    print("=" * 60)
    print("Example 16: Sampling Filter")
    print("=" * 60)
    
    import random
    
    class SamplingFilter:
        """Filter that samples a percentage of messages"""
        
        def __init__(self, sample_rate=0.1):
            """
            sample_rate: float between 0.0 and 1.0
                        0.1 = 10% of messages, 0.5 = 50%, etc.
            """
            self.sample_rate = sample_rate
        
        def __call__(self, record):
            return random.random() < self.sample_rate
    
    logger = Logger()
    
    # Sample 20% of messages (useful for high-volume logs)
    sampling_filter = SamplingFilter(sample_rate=0.2)
    
    logger.add(sys.stdout, level="INFO", filter=sampling_filter, format="{level} | {message}")
    
    print("Logging 20 messages with 20% sampling (expect ~4 to show):")
    for i in range(1, 21):
        logger.info(f"Message {i}")
    
    print()


def main():
    """Run all examples"""
    examples = [
        example_1_basic_filter,
        example_2_lambda_filter,
        example_3_level_filter,
        example_4_module_filter_include,
        example_5_module_filter_exclude,
        example_6_filter_with_extra_fields,
        example_7_multiple_handlers_different_filters,
        example_8_custom_filter_class,
        example_9_combining_filters_and,
        example_10_combining_filters_or,
        example_11_rate_limiting_filter,
        example_12_time_based_filter,
        example_13_complex_filter_combination,
        example_14_performance_filter,
        example_15_environment_filter,
        example_16_sampling_filter,
    ]
    
    for example in examples:
        example()
        input("Press Enter to continue to next example...")
        print("\n\n")


if __name__ == "__main__":
    main()

