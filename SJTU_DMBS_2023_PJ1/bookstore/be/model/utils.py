import time

def out_of_time_check(order_time:float) -> bool:
    if time.time()-order_time>10:
        return True
    return False