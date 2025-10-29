"""
Quick demo of MyLogger Day 4 implementation

Run this to see the logger in action!
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from mylogger import logger


def main():
    print("\n" + "=" * 70)
    print(" " * 20 + "*** MyLogger - Day 4 Demo ***")
    print("=" * 70 + "\n")
    
    # Demo 1: All log levels
    print("[Demo 1] All Log Levels")
    print("-" * 70)
    logger.trace("TRACE: Very detailed debugging info")
    logger.debug("DEBUG: Debugging information")
    logger.info("INFO: General information")
    logger.success("SUCCESS: Operation completed!")
    logger.warning("WARNING: Something to watch out for")
    logger.error("ERROR: Something went wrong")
    logger.critical("CRITICAL: Urgent attention needed!")
    print()
    
    # Demo 2: Formatting magic
    print("[Demo 2] Flexible Message Formatting")
    print("-" * 70)
    
    # Positional
    logger.info("User {} just signed up", "Alice")
    
    # Named
    logger.info("Payment of ${amount:.2f} processed", amount=149.99)
    
    # Mixed
    logger.info("{} connected from {country}", "Bob", country="Canada")
    print()
    
    # Demo 3: Extra context
    print("[Demo 3] Extra Context for Structured Logging")
    print("-" * 70)
    logger.info("User authentication successful",
                user_id=12345,
                email="alice@example.com",
                login_method="oauth",
                ip_address="192.168.1.100")
    print()
    
    # Demo 4: Real-world scenario
    print("[Demo 4] Real-World Web Server Scenario")
    print("-" * 70)
    
    def handle_request(method, path, user_id):
        logger.info("Incoming {} request to {}", method, path,
                   user_id=user_id,
                   timestamp="2024-01-15T10:30:00")
        
        if path == "/admin":
            logger.warning("Unauthorized admin access attempt",
                          user_id=user_id,
                          path=path)
            return False
        
        logger.success("Request processed successfully",
                      user_id=user_id,
                      path=path,
                      duration_ms=42)
        return True
    
    handle_request("GET", "/api/users", user_id=100)
    handle_request("POST", "/admin", user_id=200)
    print()
    
    # Demo 5: Error handling
    print("[Demo 5] Graceful Error Handling")
    print("-" * 70)
    
    def risky_operation():
        try:
            result = 10 / 0
        except ZeroDivisionError as e:
            logger.error("Division by zero in calculation",
                        exception=e,
                        operation="divide",
                        numerator=10,
                        denominator=0)
    
    risky_operation()
    print()
    
    # Demo 6: Using log() method
    print("[Demo 6] Dynamic Log Levels")
    print("-" * 70)
    
    # String level
    logger.log("INFO", "Using log() with string level")
    
    # Numeric level
    logger.log(40, "Using log() with numeric level (40 = ERROR)")
    print()
    
    print("=" * 70)
    print(" " * 15 + "*** Day 4 Implementation Complete! ***")
    print("=" * 70)
    print()
    print("Features implemented:")
    print("  [X] All 7 log levels (TRACE to CRITICAL)")
    print("  [X] Flexible message formatting (positional, named, mixed)")
    print("  [X] Automatic caller context (file, function, line)")
    print("  [X] Process and thread information")
    print("  [X] Extra context for structured logging")
    print("  [X] Exception handling")
    print("  [X] Thread-safe operations")
    print()
    print("Coming next in Day 5:")
    print("  [ ] Handler management (file, console, callable)")
    print("  [ ] Multiple output destinations")
    print("  [ ] Handler-level filtering")
    print()
    print("Note: Logs appear in stderr (above) with format:")
    print("      [LEVEL] message (filename:function:line)")
    print()


if __name__ == "__main__":
    main()

