import time
import sys

log_file = "scan_db_output.log"


while True:
    print("Running scan_db...")
    time.sleep(5)
    sys.stdout = open(log_file, "a")
    sys.stderr = sys.stdout



