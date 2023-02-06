import sys
import os

if sys.argv[1] == "create":
    os.system(f"python3 scripts/create.py")
elif sys.argv[1] == "delete":
    os.system(f"python3 scripts/delete.py")
elif sys.argv[1] == "activate":
    os.system(f"python3 scripts/activate.py")
elif sys.argv[1] == "deactivate":
    os.system(f"python3 scripts/deactivate.py")
elif sys.argv[1] == "view":
    os.system(f"python3 scripts/view.py")