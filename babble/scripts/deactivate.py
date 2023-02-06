import os
import util
import subprocess

from yaspin import yaspin

projects = sorted(os.listdir("/projects"))

if len(projects) == 0:
    print("\n> no projects found\n")
    exit()

project = util.prompt(projects, "select a project", "ctrl-c to cancel")

if os.path.exists(f"/projects/{project}/aws/url") or True:
    print()
    os.system("aws configure")
    print()
    spinner = yaspin(text="applying changes...").simpleDots
    spinner.start()
    # subprocess.run(f"terraform -chdir=/projects/{project}/aws destroy -auto-approve", shell=True, capture_output=True)
    os.system(f"terraform -chdir=/projects/{project}/aws destroy -auto-approve")
    spinner.stop()
    os.system
else:
    print("\n> project not active\n")