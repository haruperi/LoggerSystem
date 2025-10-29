"""
Context Binding Examples

This module demonstrates mylogger's context binding features:
- Global extra context
- BoundLogger for automatic context inclusion
- Context managers for temporary context
- Chaining bound loggers
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import mylogger
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mylogger import Logger


def example_1_global_extra():
    """Example 1: Global logger extra context"""
    print("\n" + "=" * 70)
    print("Example 1: Global Extra Context")
    print("=" * 70)

    logger = Logger()
    logger.add(
        sys.stderr,
        level="INFO",
        format="{time:HH:mm:ss} | {level: <8} | {message} | app_version={extra.app_version}",
    )

    # Set global extra that applies to all log calls
    logger.extra["app_version"] = "1.2.3"

    print("Setting global app_version in logger.extra...")
    logger.info("Application started")
    logger.info("Loading configuration")
    logger.info("Ready to accept requests")

    print("\n[OK] All logs include app_version from global extra")


def example_2_bind_basic():
    """Example 2: Basic bind() usage"""
    print("\n" + "=" * 70)
    print("Example 2: Basic Bind Usage")
    print("=" * 70)

    logger = Logger()
    logger.add(
        sys.stderr,
        level="INFO",
        format="{time:HH:mm:ss} | {message} | request_id={extra.request_id}",
    )

    print("Creating bound logger for a specific request...")

    # Create a bound logger for this specific request
    request_logger = logger.bind(request_id="REQ-12345")

    request_logger.info("Received request")
    request_logger.info("Processing payment")
    request_logger.info("Request completed")

    print("\n[OK] All logs from bound logger include request_id")


def example_3_bind_chaining():
    """Example 3: Chaining bind() calls"""
    print("\n" + "=" * 70)
    print("Example 3: Bind Chaining")
    print("=" * 70)

    logger = Logger()
    logger.add(
        sys.stderr,
        level="INFO",
        format="{message} | user={extra.user_id} | session={extra.session_id} | op={extra.operation}",
    )

    print("Creating progressively more specific bound loggers...")

    # Start with user context
    user_logger = logger.bind(user_id="USER-999")
    user_logger.info("User logged in")

    # Add session context
    session_logger = user_logger.bind(session_id="SESS-ABC123")
    session_logger.info("Session created")

    # Add operation context
    checkout_logger = session_logger.bind(operation="checkout")
    checkout_logger.info("Starting checkout")
    checkout_logger.info("Processing payment")
    checkout_logger.info("Checkout complete")

    print("\n[OK] Context accumulates through chaining")


def example_4_contextualize():
    """Example 4: Using contextualize() for temporary context"""
    print("\n" + "=" * 70)
    print("Example 4: Contextualize (Temporary Context)")
    print("=" * 70)

    logger = Logger()
    logger.add(sys.stderr, level="INFO", format="{message} | request_id={extra.request_id}")

    print("Using context manager for temporary context...")

    logger.info("Before context")

    # Temporary context for this block
    with logger.contextualize(request_id="REQ-TEMP-001"):
        logger.info("Inside context 1")
        logger.info("Processing request 1")

    logger.info("Between contexts")

    with logger.contextualize(request_id="REQ-TEMP-002"):
        logger.info("Inside context 2")
        logger.info("Processing request 2")

    logger.info("After contexts")

    print("\n[OK] Context is automatically removed after 'with' block")


def example_5_nested_contextualize():
    """Example 5: Nested context managers"""
    print("\n" + "=" * 70)
    print("Example 5: Nested Context Managers")
    print("=" * 70)

    logger = Logger()
    logger.add(
        sys.stderr, level="INFO", format="{message} | req={extra.request_id} | task={extra.task_id}"
    )

    print("Using nested context managers...")

    with logger.contextualize(request_id="REQ-OUTER"):
        logger.info("Outer context")

        with logger.contextualize(task_id="TASK-001"):
            logger.info("Inner context - has both request and task")

        logger.info("Back to outer context - only request")

    logger.info("Outside all contexts")

    print("\n[OK] Nested contexts work correctly")


def example_6_web_request_simulation():
    """Example 6: Simulating web request handling"""
    print("\n" + "=" * 70)
    print("Example 6: Web Request Simulation")
    print("=" * 70)

    logger = Logger()
    logger.add(
        sys.stderr,
        level="INFO",
        format="{time:HH:mm:ss} | [{extra.request_id}] {extra.method} {extra.path} | {message}",
    )

    def handle_request(request_id, method, path, user_id):
        """Simulate handling a web request"""
        # Create request-specific logger
        req_logger = logger.bind(request_id=request_id, method=method, path=path, user_id=user_id)

        req_logger.info("Request received")
        req_logger.info("Authenticating user")
        req_logger.info("Executing handler")
        req_logger.info("Sending response")

    print("Simulating multiple web requests...")

    handle_request("REQ-001", "GET", "/api/users", "alice")
    handle_request("REQ-002", "POST", "/api/orders", "bob")
    handle_request("REQ-003", "DELETE", "/api/sessions", "charlie")

    print("\n[OK] Each request has its own context")


def example_7_database_transaction():
    """Example 7: Database transaction logging"""
    print("\n" + "=" * 70)
    print("Example 7: Database Transaction Logging")
    print("=" * 70)

    logger = Logger()
    logger.add(sys.stderr, level="DEBUG", format="{level: <8} | [{extra.transaction_id}] {message}")

    def execute_transaction(transaction_id):
        """Simulate a database transaction"""
        tx_logger = logger.bind(transaction_id=transaction_id)

        tx_logger.debug("Beginning transaction")
        tx_logger.debug("Acquiring lock on users table")
        tx_logger.debug("Updating user record")
        tx_logger.debug("Updating audit log")
        tx_logger.info("Transaction committed successfully")

    print("Executing database transactions...")

    execute_transaction("TX-9001")
    execute_transaction("TX-9002")
    execute_transaction("TX-9003")

    print("\n[OK] Each transaction has clear context")


def example_8_background_jobs():
    """Example 8: Background job processing"""
    print("\n" + "=" * 70)
    print("Example 8: Background Job Processing")
    print("=" * 70)

    logger = Logger()
    logger.add(
        sys.stderr,
        level="INFO",
        format="{message} | job_id={extra.job_id} | job_type={extra.job_type}",
    )

    def process_job(job_id, job_type, data):
        """Simulate processing a background job"""
        job_logger = logger.bind(job_id=job_id, job_type=job_type)

        job_logger.info("Job started")
        job_logger.info(f"Processing data: {data}")
        job_logger.info("Job completed")

    print("Processing background jobs...")

    process_job("JOB-001", "email", {"to": "user@example.com"})
    process_job("JOB-002", "report", {"format": "PDF"})
    process_job("JOB-003", "cleanup", {"older_than": "30 days"})

    print("\n[OK] Jobs are easily trackable with context")


def example_9_context_override():
    """Example 9: Context priority and override"""
    print("\n" + "=" * 70)
    print("Example 9: Context Priority and Override")
    print("=" * 70)

    logger = Logger()
    logger.add(sys.stderr, level="INFO", format="{message} | key={extra.key}")

    # Global extra
    logger.extra["key"] = "global_value"

    print("Testing context priority: call > bound > global")

    logger.info("Using global context")

    # Bound context overrides global
    bound = logger.bind(key="bound_value")
    bound.info("Using bound context")

    # Per-call extra overrides bound
    bound.info("Using call context", extra={"key": "call_value"})

    print("\n[OK] Context priority works as expected")


def example_10_multi_handler_context():
    """Example 10: Context with multiple handlers"""
    print("\n" + "=" * 70)
    print("Example 10: Context with Multiple Handlers")
    print("=" * 70)

    log_dir = Path("logs_context_example")
    log_dir.mkdir(exist_ok=True)

    logger = Logger()

    # Console handler (with color)
    logger.add(
        sys.stderr,
        level="INFO",
        format="{time:HH:mm:ss} | {level: <8} | {message} | user={extra.user_id}",
        colorize=True,
    )

    # File handler (without color)
    logger.add(
        str(log_dir / "app.log"),
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | user={extra.user_id} | {message}",
        colorize=False,
    )

    print(f"Logging to console and file: {log_dir / 'app.log'}")

    # Use bound logger
    user_logger = logger.bind(user_id="USER-777")

    user_logger.debug("Debug message (file only)")
    user_logger.info("Info message (both console and file)")
    user_logger.warning("Warning message (both)")

    print(f"\n[OK] Context is preserved across all handlers")
    print(f"Check {log_dir / 'app.log'} for file output")


def example_11_real_world_api():
    """Example 11: Real-world API endpoint handler"""
    print("\n" + "=" * 70)
    print("Example 11: Real-World API Endpoint")
    print("=" * 70)

    logger = Logger()
    logger.add(
        sys.stderr,
        level="INFO",
        format="{time:HH:mm:ss} | [{extra.request_id}] {level: <7} | {message}",
        colorize=True,
    )

    def api_create_order(request_id, user_id, items):
        """Simulate an API endpoint that creates an order"""
        # Create request-specific logger
        req_logger = logger.bind(request_id=request_id, user_id=user_id)

        req_logger.info("POST /api/orders - Request received")

        # Use contextualize for the order creation phase
        with req_logger.contextualize(operation="create_order"):
            req_logger.info("Validating items")

            if not items:
                req_logger.error("Validation failed: No items provided")
                return

            req_logger.info(f"Creating order with {len(items)} items")

            # Create order-specific logger
            order_id = "ORD-99999"
            order_logger = req_logger.bind(order_id=order_id)

            order_logger.info("Order created")
            order_logger.info("Calculating total")
            order_logger.info("Processing payment")
            order_logger.success("Payment successful")
            order_logger.info("Sending confirmation email")

        req_logger.info("Response sent: 201 Created")

    print("Simulating API endpoint call...")

    api_create_order(
        request_id="REQ-API-001", user_id="USER-123", items=[{"product": "Widget", "qty": 2}]
    )

    print("\n[OK] Complex API flow with nested context")


def main():
    print("=" * 70)
    print("Context Binding Examples - MyLogger")
    print("=" * 70)

    example_1_global_extra()
    example_2_bind_basic()
    example_3_bind_chaining()
    example_4_contextualize()
    example_5_nested_contextualize()
    example_6_web_request_simulation()
    example_7_database_transaction()
    example_8_background_jobs()
    example_9_context_override()
    example_10_multi_handler_context()
    example_11_real_world_api()

    print("\n" + "=" * 70)
    print("[OK] All context binding examples completed!")
    print("=" * 70)

    print("\nKey Features Demonstrated:")
    print("  - Global extra context (logger.extra)")
    print("  - BoundLogger with logger.bind()")
    print("  - Chaining bound loggers")
    print("  - Temporary context with logger.contextualize()")
    print("  - Nested context managers")
    print("  - Context priority (call > bound > global)")
    print("  - Real-world patterns for web apps, databases, and APIs")


if __name__ == "__main__":
    main()
