import os
import util
import shutil
import subprocess

from yaspin import yaspin

projects = sorted(os.listdir("/projects"))

if len(projects) == 0:
    print("\n> no projects found\n")
    exit()

project = util.prompt(projects, "select a project to delete", "ctrl-c to cancel")
print()
if os.path.exists(f"/projects/{project}/aws/url"):
    os.system("aws configure")
    print()
    spinner = yaspin(text="applying changes...").simpleDots
    spinner.start()
    subprocess.run(f"terraform -chdir=/projects/{project}/aws destroy -auto-approve", shell=True, capture_output=True)
    spinner.write("> changes applied")
    if os.path.exists(f"/projects/{project}/aws/url"):
        os.remove(f"/projects/{project}/aws/url")
    spinner.stop()
spinner = yaspin(text="deleting project...").simpleDots
spinner.start()
shutil.rmtree(f"/projects/{project}")
spinner.write("> project deleted")
spinner.stop()

print()
