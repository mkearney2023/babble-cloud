import os
import re
import yaml
import util
import shutil
import string
import random
import subprocess

from yaspin import yaspin

# CONFIGURING YAML FORMATTING
def represent_none(self, _):
    return self.represent_scalar('tag:yaml.org,2002:null', '~')
yaml.add_representer(type(None), represent_none)
def represent_str(dumper, data):
  if len(data.splitlines()) > 1:
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
  return dumper.represent_scalar('tag:yaml.org,2002:str', data)
yaml.add_representer(str, represent_str)

# FUNCTION TO GENERATE UNIQUE IDENTIFIER
def id():
    return ''.join(random.choices(string.ascii_lowercase, k=36))

projects = sorted(os.listdir("/projects"))

if len(projects) == 0:
    print("\n> no projects found\n")
    exit()

project = util.prompt(projects, "select a project to activate", "ctrl-c to cancel")

# SETTING CREDENTIALS
print()
os.system("aws configure")
print()

spinner = yaspin(text="loading project state...").simpleDots
spinner.start()

state = {}
config = {}
if not os.path.exists(f"/projects/{project}/state.yaml"):
    os.system(f"touch /projects/{project}/state.yaml")
with open(f"/projects/{project}/state.yaml", "r") as f:
    state = yaml.safe_load(f)
    if state is None:
        state = {
            "id": id(),
            "folders": {},
            "tables": {},
            "packages": {},
            "modules": {},
            "endpoints": {}
        }
with open(f"/projects/{project}/config.yaml", "r") as f:
    config = yaml.safe_load(f)

spinner.write("> project state loaded")
spinner.text = "updating tables..."

update_tables = False
for k, v in config["tables"].items():
    if k not in state["tables"].keys():
        state["tables"][k] = v
        state["tables"][k]["id"] = id()
        update_tables = True
    elif v["key"] != state["tables"][k]["key"]:
        state["tables"][k]["key"] = v["key"]
for k, v in state["tables"].copy().items():
    if k not in config["tables"].keys():
        del state["tables"][k]
        update_tables = True

spinner.write("> tables updated")
spinner.text = "updating folders..."

update_folders = False
for k, v in config["folders"].items():
    if k not in state["folders"].keys():
        state["folders"][k] = {}
        state["folders"][k]["id"] = id()
        update_folders = True
for k, v in state["folders"].copy().items():
    if k not in config["folders"].keys():
        del state["folders"][k]
        update_folders = True

spinner.write("> folders updated")
spinner.text = "updating modules..."

update_modules = False
for k, v in config["modules"].items():
    if k not in state["modules"].keys():
        state["modules"][k] = v
        state["modules"][k]["id"] = id()
        update_modules = True
    elif v["content"] != state["modules"][k]["content"]:
        state["modules"][k]["content"] = v["content"]
        update_modules = True
for k, v in state["modules"].copy().items():
    if k not in config["modules"].keys():
        del state["modules"][k]
        update_modules = True

spinner.write("> modules updated")
spinner.text = "updating endpoints..."

update_endpoints = False
for k, v in config["endpoints"].items():
    if k not in state["endpoints"].keys():
        state["endpoints"][k] = v
        state["endpoints"][k]["id"] = id()
        state["endpoints"][k]["method"] = k.split(" ")[0]
        state["endpoints"][k]["path"] = k.split(" ")[1]
        state["endpoints"][k]["path_specs"] = re.sub(r'{[^}]*}*', '{}', k.split(" ")[1]).split("/")[1:]
        state["endpoints"][k]["path_parameters"] = re.findall(r'{([^{}]+)}', k.split(" ")[1])
        update_endpoints = True
    elif v["content"] != state["endpoints"][k]["content"]:
        state["endpoints"][k]["content"] = v["content"]
        update_endpoints = True
for k, v in state["endpoints"].copy().items():
    if k not in config["endpoints"].keys():
        del state["endpoints"][k]
        update_endpoints = True

spinner.write("> endpoints updated")
spinner.text = "updating packages..."

update_packages = False
update_pip_packages = False
for k, v in config["packages"].items():
    if k not in state["packages"].keys():
        state["packages"][k] = v
        update_packages = True
        if v["source"] == "pip":
            update_pip_packages = True
        else:
            state["packages"][k]["modules"] = [k]
    elif v["version"] != state["packages"][k]["version"]:
        state["packages"][k]["version"] = v["version"]
        if v["source"] == "pip":
            update_pip_packages = True
for k, v in state["packages"].copy().items():
    if k not in config["packages"].keys():
        del state["packages"][k]
        update_packages = True
        if v["source"] == "pip":
            update_pip_packages = True
if update_pip_packages:
    # CREATING REQUIREMENTS.TXT
    with open(f"/projects/{project}/requirements.txt", "w") as f:
        for k, v in state["packages"].items():
            if v["source"] == "pip":
                f.write(f"{k}\n")
    # (RE)INSTALLING PIP PACKAGES
    if os.path.exists(f"/projects/{project}/packages/python"):
        shutil.rmtree(f"/projects/{project}/packages/python")
    os.system(f"mkdir -p /projects/{project}/packages/python")
    subprocess.run(f"pip3 install -t /projects/{project}/packages/python -r /projects/{project}/requirements.txt", shell=True, capture_output=True)
    for file in os.listdir(f"/projects/{project}/packages/python"):
        # READING DIST-INFO DIRECTORIES
        if file.endswith(".dist-info"):
            # GETTING PACKAGE NAME FROM METADATA FILE
            package_name = ""
            if os.path.exists(f"/projects/{project}/packages/python/{file}/METADATA"):
                with open(f"/projects/{project}/packages/python/{file}/METADATA", "r") as f:
                    for line in f.readlines():
                        if line.startswith("Name: "):
                            package_name = line.split(":")[1].strip().lower(); break
            # GETTING MODULE NAME(S) FROM TOP_LEVEL.TXT FILE
            if state["packages"].get(package_name) is not None:
                state["packages"][package_name]["modules"] = []
                if os.path.exists(f"/projects/{project}/packages/python/{file}/top_level.txt"):
                    with open(f"/projects/{project}/packages/python/{file}/top_level.txt", "r") as f:
                        for line in f.readlines():
                            state["packages"][package_name]["modules"].append(line.strip())
                state["packages"][package_name]["modules"].sort()

spinner.write("> packages updated")
spinner.text = "loading boilerplate code..."

if update_tables or update_folders or update_modules or update_packages or update_endpoints:
    # CREATING SOURCE CODE FOR PYTHON MODULES
    for k1, v1 in state["modules"].items():
        state["modules"][k1]["source"] = "\n".join([
            "\n".join([f"import {v2['id']} as {k2}" for k2, v2 in state["modules"].items() if k1 != k2]),
            "\n".join([f"import {', '.join([m for m in v2['modules']])}" for k2, v2 in state["packages"].items()]),
            "\n".join([f"import {v2['id']}" for k2, v2 in state["tables"].items()]),
            "\n".join([f"{k2} = {v2['id']}.Module()" for k2, v2 in state["tables"].items()]),
            "\n".join([f"import {v2['id']}" for k2, v2 in state["folders"].items()]),
            "\n".join([f"{k2} = {v2['id']}.Module()" for k2, v2 in state["folders"].items()]),
            v1["content"]
        ])
    # CREATING SOURCE CODE FOR PYTHON ENDPOINTS
    for k1, v1 in state["endpoints"].items():
        state["endpoints"][k1]["source"] = "\n".join([
            "\n".join([f"import {v2['id']} as {k2}" for k2, v2 in state["modules"].items()]),
            "\n".join([f"import {', '.join([m for m in v2['modules']])}" for k2, v2 in state["packages"].items()]),
            "\n".join([f"import {v2['id']}" for k2, v2 in state["tables"].items()]),
            "\n".join([f"{k2} = {v2['id']}.Module()" for k2, v2 in state["tables"].items()]),
            "\n".join([f"import {v2['id']}" for k2, v2 in state["folders"].items()]),
            "\n".join([f"{k2} = {v2['id']}.Module()" for k2, v2 in state["folders"].items()]),
            v1["content"]
        ])
    # UPDATING STATE FILE
    with open(f"/projects/{project}/state.yaml", "w") as f:
        yaml.dump(state, f, default_flow_style=False)
    shutil.copy(f"/projects/{project}/state.yaml", f"/projects/{project}/aws/state.yaml")

spinner.write("> boilerplate code loaded")
spinner.text = "updating project state..."

spinner.write("> project state updated")
spinner.text = "initializing terraform..."
subprocess.run(f"terraform -chdir=/projects/{project}/aws init", shell=True, capture_output=True)
spinner.write("> terraform initialized")
spinner.text = "applying changes..."
subprocess.run(f"terraform -chdir=/projects/{project}/aws apply -auto-approve", shell=True, capture_output=True)
spinner.write("> changes applied")
spinner.stop()

# DISPLAYING INVOKE URL TO USER
if os.path.exists(f"/projects/{project}/aws/url"):
    with open(f"/projects/{project}/aws/url", "r") as f:
        print(f"\n{project} successfully activated ({f.read()})\n")