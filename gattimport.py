import sys
import traceback
print("Importing Gattlib")
try:
    from gattlib import GATTRequester
    print("Success importing Gattlib")
except Exception:
    print("Failure import Gattlib")
    traceback.print_exc(file=sys.stdout)
print("DONE")
