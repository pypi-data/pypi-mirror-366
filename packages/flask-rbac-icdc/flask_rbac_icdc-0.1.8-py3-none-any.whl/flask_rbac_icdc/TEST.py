from flask_rbac_icdc.rbac import RBAC
import os
import time

def measure_time_ms(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        elapsed_ms = (end - start) * 1000
        print(f"Execution time for {func.__name__}: {elapsed_ms:.2f} ms")
        return result
    return wrapper

try:
    start = time.time()
    RBAC.validate_config("D:\\ICDC_PROJ\\storage-api\\settings\\rbac.yaml")
    end = time.time()
    elapsed_ms = (end - start) * 1000
    print(f"Execution time : {elapsed_ms:.2f} ms")
    print("RBAC configuration is valid.")
except Exception as e:
    print(f"Error validating RBAC configuration: {e.message}")
