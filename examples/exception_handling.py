"""
Exception handling examples
"""

from mylogger import logger

@logger.catch
def risky_function():
    """Function that might raise an exception"""
    return 1 / 0


def manual_exception_handling():
    """Manual exception logging"""
    try:
        result = 10 / 0
    except Exception:
        logger.exception("Division by zero occurred")


def main():
    """Exception handling examples"""
    
    # Using decorator
    risky_function()
    
    # Manual handling
    manual_exception_handling()


if __name__ == "__main__":
    main()
