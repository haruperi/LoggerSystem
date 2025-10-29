"""
File rotation examples
"""

from mylogger import logger


def main():
    """File rotation examples"""

    # Size-based rotation
    logger.add("logs/app.log", rotation="10 MB", retention="7 days", compression="gz", level="INFO")

    # Time-based rotation
    logger.add("logs/daily.log", rotation="daily", retention=7, level="DEBUG")  # Keep 7 files

    # Log many messages
    for i in range(1000):
        logger.info("Log message number {}", i)


if __name__ == "__main__":
    main()
