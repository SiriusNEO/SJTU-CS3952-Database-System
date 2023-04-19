import time

ORDER_EXPIRED_TIME_INTERVAL = 10


def check_expired(timestamp: float) -> bool:
    """Check whether an order is expired."""

    if time.time() - timestamp > ORDER_EXPIRED_TIME_INTERVAL:
        return True
    return False
