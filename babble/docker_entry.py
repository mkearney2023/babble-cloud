import sys

from scripts import functions

if sys.argv[1] == "create":
    functions.create()
elif sys.argv[1] == "delete":
    functions.delete()
elif sys.argv[1] == "push":
    functions.push()
elif sys.argv[1] == "pull":
    functions.pull()
elif sys.argv[1] == "activate":
    functions.activate()
elif sys.argv[1] == "deactivate":
    functions.deactivate()
elif sys.argv[1] == "view":
    functions.view()