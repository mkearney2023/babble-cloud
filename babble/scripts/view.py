import os
import util

projects = sorted(os.listdir("/projects"))

if len(projects) == 0:
    print("\n> no projects found\n")
    exit()

project = util.prompt(projects, "select project to view", "ctrl-c to cancel")
print()
if not os.path.exists(f"/projects/{project}/config.yaml"):
    exit()
os.system(f"cat /projects/{project}/config.yaml")
print("\n")
if os.path.exists(f"/projects/{project}/aws/url"):
    os.system(f"cat /projects/{project}/aws/url")
    print("\n")