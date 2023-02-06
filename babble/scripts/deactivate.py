import os
import util
import subprocess

from yaspin import yaspin

projects = sorted(os.listdir("/projects"))

if len(projects) == 0:
    print("\n> no projects found\n")
    exit()

project = util.prompt(projects, "select a project", "ctrl-c to cancel")

if os.path.exists(f"/projects/{project}/aws/url"):
    print()
    os.system("aws configure")
    print()
    spinner = yaspin(text="applying changes...").simpleDots
    spinner.start()
    subprocess.run(f"terraform -chdir=/projects/{project}/aws destroy -auto-approve", shell=True, capture_output=True)
    spinner.write("> changes applied")
    spinner.stop()
else:
    print("\n> project not active\n")