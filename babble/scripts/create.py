import os
import shutil
import subprocess

from yaspin import yaspin

projects = sorted(os.listdir("/projects"))
if len(projects) > 0:
    print("\ncurrent projects\n")
    print("\n".join([f"  {p}" for p in projects]))
try:
    project = input("\nproject name: ")
except KeyboardInterrupt:
    exit()
print()

if project in projects:
    print("> project already exists\n")
    exit()

spinner = yaspin("copying template...").simpleDots
spinner.start()
shutil.copytree("/templates", f"/projects/{project}")
spinner.write("> template copied")
spinner.text = "initializing terraform..."
subprocess.run(f"terraform -chdir=/projects/{project}/aws init", shell=True, capture_output=True)
spinner.write("> terraform initialized")
spinner.stop()

print()