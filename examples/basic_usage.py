"""
Basic usage examples for MyLogger
"""

from mylogger import logger

def main():
    """Basic logging examples"""
    
    # Simple logging
    logger.info("Application started")
    logger.debug("Debug information")
    logger.warning("This is a warning")
    logger.error("An error occurred")
    logger.success("Operation completed successfully")
    
    # Logging with format
    name = "Alice"
    age = 30
    logger.info("User {name} is {age} years old", name=name, age=age)
    
    # Logging with positional arguments
    logger.info("Result: {}", 42)
    logger.info("Values: {} and {}", 10, 20)


if __name__ == "__main__":
    main()
