"""
Example: Using CallableHandler for Custom Log Processing

This example demonstrates how to use CallableHandler to send logs to
custom destinations like databases, message queues, APIs, or any custom processing.

CallableHandler allows you to:
1. Send formatted strings to custom functions
2. Serialize logs to JSON for structured logging
3. Integrate with external systems (databases, APIs, webhooks, etc.)
4. Process logs in real-time with custom logic
"""

import json
from mylogger import Logger, logger


def example_1_basic_callable():
    """Example 1: Basic callable handler with formatted strings"""
    print("\n" + "=" * 70)
    print("Example 1: Basic Callable Handler")
    print("=" * 70)

    # Create a list to collect logs
    collected_logs = []

    def log_collector(message):
        """Simple function that collects log messages"""
        collected_logs.append(message)
        print(f"[Collected] {message[:60]}...")

    # Create logger with callable handler
    log = Logger()
    log.add(sink=log_collector, level="DEBUG", format="{time:HH:mm:ss} | {level: <8} | {message}")

    # Log some messages
    log.info("User logged in")
    log.warning("High memory usage detected")
    log.error("Failed to connect to database")

    print(f"\n[OK] Collected {len(collected_logs)} log messages")


def example_2_serialized_json():
    """Example 2: Serialize logs to JSON for structured logging"""
    print("\n" + "=" * 70)
    print("Example 2: JSON Serialization")
    print("=" * 70)

    json_logs = []

    def json_collector(json_str):
        """Function that receives JSON-serialized logs"""
        # Parse the JSON
        data = json.loads(json_str)
        json_logs.append(data)

        # Pretty print the JSON
        print(f"\n[JSON Log Entry]")
        print(f"  Level: {data['level']['name']}")
        print(f"  Message: {data['message']}")
        print(f"  Time: {data['time']['repr']}")
        print(f"  Location: {data['file']['name']}:{data['line']}")

    # Create logger with serialization enabled
    log = Logger()
    log.add(sink=json_collector, level="INFO", serialize=True)  # Enable JSON serialization

    # Log with extra context
    log.info("Payment processed", user_id=12345, amount=99.99, currency="USD")
    log.warning("Rate limit approaching", requests=950, limit=1000)

    print(f"\n[OK] Collected {len(json_logs)} JSON log entries")


def example_3_multiple_destinations():
    """Example 3: Send logs to multiple custom destinations"""
    print("\n" + "=" * 70)
    print("Example 3: Multiple Custom Destinations")
    print("=" * 70)

    # Simulate different log destinations
    console_logs = []
    error_logs = []
    json_logs = []

    def console_handler(message):
        """Handle console output"""
        console_logs.append(message)
        print(f"[Console] {message}")

    def error_handler(message):
        """Handle errors - could send to error tracking service"""
        error_logs.append(message)
        print(f"[ERROR] {message}")

    def json_handler(json_str):
        """Handle structured logs - could send to log aggregation service"""
        json_logs.append(json_str)
        data = json.loads(json_str)
        print(f"[JSON] {data['level']['name']} - {data['message']}")

    # Create logger with multiple handlers
    log = Logger()

    # Add console handler for all logs
    log.add(sink=console_handler, level="DEBUG", format="{time:HH:mm:ss} | {level: <8} | {message}")

    # Add error handler for errors only
    log.add(
        sink=error_handler, level="ERROR", format="[ERROR] {time:YYYY-MM-DD HH:mm:ss} - {message}"
    )

    # Add JSON handler for structured logging
    log.add(sink=json_handler, level="INFO", serialize=True)

    # Log at different levels
    log.debug("Debug information")
    log.info("User action performed", action="login", user="alice")
    log.warning("Warning message")
    log.error("Critical error occurred")

    print(
        f"\n[OK] Console: {len(console_logs)} | Errors: {len(error_logs)} | JSON: {len(json_logs)}"
    )


def example_4_database_simulation():
    """Example 4: Simulate sending logs to a database"""
    print("\n" + "=" * 70)
    print("Example 4: Database Logging Simulation")
    print("=" * 70)

    # Simulate a database
    database = []

    def log_to_database(json_str):
        """Simulate inserting log into database"""
        data = json.loads(json_str)

        # Create database record
        db_record = {
            "id": len(database) + 1,
            "timestamp": data["time"]["timestamp"],
            "level": data["level"]["name"],
            "message": data["message"],
            "module": data["module"],
            "function": data["function"],
            "line": data["line"],
            "extra": data["extra"],
        }

        database.append(db_record)
        print(
            f"[DB] Inserted: ID={db_record['id']}, Level={db_record['level']}, Message={db_record['message'][:40]}..."
        )

    # Create logger
    log = Logger()
    log.add(sink=log_to_database, level="INFO", serialize=True)

    # Log various events
    log.info("User registered", user_id=101, email="user@example.com")
    log.info("Order placed", order_id=1001, total=150.00)
    log.warning("Low stock alert", product_id=501, quantity=5)
    log.error("Payment failed", transaction_id="tx_123", reason="insufficient_funds")

    # Query the "database"
    print(f"\n[Database Contents] ({len(database)} records):")
    for record in database:
        print(f"  [{record['id']}] {record['level']}: {record['message']}")


def example_5_webhook_simulation():
    """Example 5: Simulate sending logs to a webhook"""
    print("\n" + "=" * 70)
    print("Example 5: Webhook Notification Simulation")
    print("=" * 70)

    webhooks_sent = []

    def send_to_webhook(json_str):
        """Simulate sending log to webhook (e.g., Slack, Discord, Teams)"""
        data = json.loads(json_str)

        # Create webhook payload
        webhook_payload = {
            "text": f"{data['level']['name']}: {data['message']}",
            "level": data["level"]["name"],
            "timestamp": data["time"]["repr"],
            "details": data["extra"],
        }

        webhooks_sent.append(webhook_payload)

        # Simulate sending to webhook
        print(f"[Webhook] Sent: {webhook_payload['text']}")
        if webhook_payload["details"]:
            print(f"   Details: {webhook_payload['details']}")

    # Create logger for critical events only
    log = Logger()
    log.add(sink=send_to_webhook, level="WARNING", serialize=True)  # Only send warnings and above

    # Log various events
    log.info("Normal operation")  # Won't trigger webhook
    log.warning("Service degradation detected", service="api", latency_ms=1200)
    log.error("Service outage", service="database", downtime_seconds=30)
    log.critical("Security breach detected", source_ip="192.168.1.100", attack_type="SQL injection")

    print(f"\n[OK] Sent {len(webhooks_sent)} webhook notifications")


def example_6_lambda_and_class_methods():
    """Example 6: Using lambda functions and class methods"""
    print("\n" + "=" * 70)
    print("Example 6: Lambda Functions and Class Methods")
    print("=" * 70)

    # Using lambda function
    log1 = Logger()
    log1.add(sink=lambda msg: print(f"[Lambda] {msg}"), level="INFO", format="{level} - {message}")

    log1.info("Hello from lambda handler!")

    # Using class method
    class LogAnalyzer:
        def __init__(self):
            self.log_count = 0
            self.error_count = 0

        def analyze_log(self, json_str):
            """Analyze incoming logs"""
            data = json.loads(json_str)
            self.log_count += 1

            if data["level"]["name"] in ["ERROR", "CRITICAL"]:
                self.error_count += 1

            print(
                f"[Analyzed] {data['message'][:40]}... (Total: {self.log_count}, Errors: {self.error_count})"
            )

        def get_stats(self):
            return {
                "total_logs": self.log_count,
                "errors": self.error_count,
                "error_rate": self.error_count / self.log_count if self.log_count > 0 else 0,
            }

    analyzer = LogAnalyzer()

    log2 = Logger()
    log2.add(sink=analyzer.analyze_log, level="DEBUG", serialize=True)

    # Generate some logs
    log2.debug("Debug message")
    log2.info("Info message")
    log2.warning("Warning message")
    log2.error("Error message")
    log2.critical("Critical message")

    # Get statistics
    stats = analyzer.get_stats()
    print(f"\n[Log Statistics]")
    print(f"   Total Logs: {stats['total_logs']}")
    print(f"   Errors: {stats['errors']}")
    print(f"   Error Rate: {stats['error_rate']:.1%}")


def example_7_filtering_and_processing():
    """Example 7: Custom filtering and processing"""
    print("\n" + "=" * 70)
    print("Example 7: Custom Filtering and Processing")
    print("=" * 70)

    processed_logs = []

    def process_high_priority_logs(json_str):
        """Process only high-priority logs with custom fields"""
        data = json.loads(json_str)

        # Extract relevant information
        priority = data["extra"].get("priority", "normal")

        if priority == "high":
            processed_logs.append(
                {"message": data["message"], "time": data["time"]["repr"], "priority": priority}
            )
            print(f"[High Priority] {data['message']}")

    log = Logger()
    log.add(
        sink=process_high_priority_logs,
        level="INFO",
        serialize=True,
        filter=lambda record: record.extra.get("priority")
        == "high",  # Filter for high priority only
    )

    # Log with different priorities
    log.info("Regular task completed", priority="normal")
    log.info("Important operation started", priority="high")
    log.info("Another regular task", priority="normal")
    log.warning("Critical system check failed", priority="high")
    log.info("Routine maintenance", priority="low")

    print(f"\n[OK] Processed {len(processed_logs)} high-priority logs")


def example_8_real_world_use_case():
    """Example 8: Real-world use case - E-commerce application"""
    print("\n" + "=" * 70)
    print("Example 8: Real-World E-commerce Application")
    print("=" * 70)

    # Different log destinations
    audit_trail = []
    error_alerts = []
    analytics_events = []

    def audit_logger(json_str):
        """Log important user actions for audit trail"""
        data = json.loads(json_str)
        audit_trail.append(
            {
                "timestamp": data["time"]["repr"],
                "action": data["extra"].get("action"),
                "user_id": data["extra"].get("user_id"),
                "details": data["message"],
            }
        )

    def error_alerter(message):
        """Alert on errors"""
        error_alerts.append(message)
        print(f"[ALERT] {message}")

    def analytics_tracker(json_str):
        """Track events for analytics"""
        data = json.loads(json_str)
        event_type = data["extra"].get("event_type")
        if event_type:
            analytics_events.append(
                {"event": event_type, "timestamp": data["time"]["timestamp"], "data": data["extra"]}
            )

    # Setup logger with multiple handlers
    log = Logger()

    # Audit trail (serialized for database storage)
    log.add(sink=audit_logger, level="INFO", serialize=True, filter=lambda r: "action" in r.extra)

    # Error alerts (formatted for human reading)
    log.add(sink=error_alerter, level="ERROR", format="[{time:HH:mm:ss}] {level}: {message}")

    # Analytics (serialized for data processing)
    log.add(
        sink=analytics_tracker,
        level="INFO",
        serialize=True,
        filter=lambda r: "event_type" in r.extra,
    )

    # Simulate e-commerce operations
    print("\n[E-commerce Operations]\n")

    log.info("User logged in", action="login", user_id=12345, event_type="user_login")

    log.info(
        "Product added to cart",
        action="add_to_cart",
        user_id=12345,
        product_id=999,
        event_type="add_to_cart",
    )

    log.info(
        "Order placed",
        action="place_order",
        user_id=12345,
        order_id=5001,
        total=299.99,
        event_type="purchase",
    )

    log.error("Payment processing failed", user_id=12345, order_id=5001, error_code="CARD_DECLINED")

    log.info(
        "Order cancelled",
        action="cancel_order",
        user_id=12345,
        order_id=5001,
        event_type="order_cancelled",
    )

    # Show summary
    print(f"\n[Summary]")
    print(f"   Audit Trail Entries: {len(audit_trail)}")
    print(f"   Error Alerts: {len(error_alerts)}")
    print(f"   Analytics Events: {len(analytics_events)}")

    print(f"\n[Audit Trail]")
    for entry in audit_trail:
        print(f"   {entry['timestamp']}: {entry['action']} by user {entry['user_id']}")

    print(f"\n[Analytics Events]")
    for event in analytics_events:
        print(f"   {event['event']}: {event['data']}")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("CallableHandler Examples - Custom Log Processing")
    print("=" * 70)

    example_1_basic_callable()
    example_2_serialized_json()
    example_3_multiple_destinations()
    example_4_database_simulation()
    example_5_webhook_simulation()
    example_6_lambda_and_class_methods()
    example_7_filtering_and_processing()
    example_8_real_world_use_case()

    print("\n" + "=" * 70)
    print("[OK] All examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
