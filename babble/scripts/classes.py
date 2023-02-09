import copy
import os
import random
import re
import shutil
import string
import subprocess
import tempfile
import yaml

from yaspin import yaspin

debug = False
providers = ["aws"]

def represent_none(self, _):
    return self.represent_scalar('tag:yaml.org,2002:null', '~')
yaml.add_representer(type(None), represent_none)
def represent_str(dumper, data):
    if len(data.splitlines()) > 1:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)
yaml.add_representer(str, represent_str)

def execute(command, hidden=True):
    if debug:
        print(command)
        return subprocess.run(command, shell=True)
    else:
        return subprocess.run(command, shell=True, capture_output=hidden)
def get_id() -> str:
    return "".join(random.choices(string.ascii_letters, k=32)).lower()
def get_dist_info(path) -> dict:
    output = {}
    if os.path.exists(f"{path}/METADATA"):
        with open(f"{path}/METADATA", "r") as f:
            for line in f.readlines():
                if line.startswith("Name: "):
                    package_name = line.split(":")[1].strip().lower()
                    output[package_name] = []
        if os.path.exists(f"{path}/top_level.txt"):
            with open(f"{path}/top_level.txt", "r") as f:
                for line in sorted(f.readlines()):
                    output[package_name].append(line.strip())
    return output
def login(provider) -> None:
    if provider == "aws":
        print()
        execute("aws configure", hidden=False)
        print()

class Spinner:
    def __init__(self, content: str):
        if not debug:
            self.spinner = yaspin(text=content).simpleDots
            self.spinner.start()
    def stop(self, content: str = ""):
        if not debug:
            if content != "":
                self.spinner.write(content)
            self.spinner.stop()

class Project:
    def __init__(self):
        self.id = get_id()
        self.tables = {}
        self.folders = {}
        self.packages = {}
        self.modules = {}
        self.endpoints = {}
        self.config = {}
    def load(self, path: str) -> None:
        with open(path, "r") as f:
            state = yaml.safe_load(f)
        if state is None:
            state = {}
        self.tables = state.get("tables", {})
        self.folders = state.get("folders", {})
        self.packages = state.get("packages", {})
        self.modules = state.get("modules", {})
        self.endpoints = state.get("endpoints", {})
        self.config = state.get("config", {})
    def save(self, path: str) -> None:
        with open(path, "w") as f:
            yaml.dump({
                "id": self.id,
                "tables": self.tables,
                "folders": self.folders,
                "packages": self.packages,
                "modules": self.modules,
                "endpoints": self.endpoints,
                "config": self.config,
            }, f, default_flow_style=False)
    def update(self, path: str) -> None:
        with open(path, "r") as f:
            config = yaml.safe_load(f)
        self.config = copy.deepcopy(config)
        update_source_code = False
        update_pip_packages = False
        # updating tables
        for k, v in config["tables"].items(): # added tables
            if v is None:
                v = {}
            if k not in self.tables.keys():
                update_source_code = True
                self.tables[k] = v
                self.tables[k]["id"] = get_id()
                self.tables[k]["import"] = f"import {self.tables[k]['id']}\n{k} = {self.tables[k]['id']}.Module()"
        for k, v in copy.deepcopy(self.tables).items(): # removed tables
            if k not in config["tables"].keys():
                update_source_code = True
                del self.tables[k]
        for k1, v1 in config["tables"].items(): # updated tables
            for k2, v2 in v1.items():
                self.tables[k1][k2] = v2
        # updating folders
        for k, v in config["folders"].items(): # added folders
            if v is None:
                v = {}
            if k not in self.folders.keys():
                update_source_code = True
                self.folders[k] = v
                self.folders[k]["id"] = get_id()
                self.folders[k]["import"] = f"import {self.folders[k]['id']}\n{k} = {self.folders[k]['id']}.Module()"
        for k, v in copy.deepcopy(self.folders).items(): # removed folders
            if k not in config["folders"].keys():
                update_source_code = True
                del self.folders[k]
        for k1, v1 in config["folders"].items(): # updated folders
            if v1 is None:
                v1 = {}
            for k2, v2 in v1.items():
                self.folders[k1][k2] = v2
        # updating packages
        for k, v in config["packages"].items(): # added packages
            if k not in self.packages.keys():
                update_source_code = True
                self.packages[k] = v
                self.packages[k]["id"] = get_id()
                if v["source"] == "pip":
                    update_pip_packages = True
                    if v.get("version") is None:
                        self.packages[k]["label"] = k
                    else:
                        self.packages[k]["label"] = f"{k}=={v['version']}"
                if v["source"] == "lib":
                    self.packages[k]["import"] = f"import {k}"
        for k, v in copy.deepcopy(self.packages).items(): # removed packages
            if k not in config["packages"].keys():
                update_source_code = True
                del self.packages[k]
        for k, v in config["packages"].items(): # updated packages
            if v["source"] != self.packages[k].get("source") or v.get("version") != self.packages[k].get("version"):
                update_source_code = True
                update_pip_packages = True
                self.packages[k]["version"] = v["version"]
                self.packages[k]["source"] = v["source"]
        # updating modules
        for k, v in config["modules"].items(): # added modules
            if v is None:
                v = {}
            if k not in self.modules.keys():
                update_source_code = True
                self.modules[k] = v
                self.modules[k]["id"] = get_id()
                self.modules[k]["import"] = f"import {self.modules[k]['id']} as {k}"
        for k, v in copy.deepcopy(self.modules).items(): # removed modules
            if k not in config["modules"].keys():
                update_source_code = True
                del self.modules[k]
        for k1, v1 in config["modules"].items(): # updated modules
            for k2, v2 in v1.items():
                self.modules[k1][k2] = v2
        # updating endpoints
        for k, v in config["endpoints"].items(): # added endpoints
            if v is None:
                v = {}
            if k not in self.endpoints.keys():
                self.endpoints[k] = v
                self.endpoints[k]["id"] = get_id()
                self.endpoints[k]["method"] = k.split(" ")[0]
                self.endpoints[k]["path"] = k.split(" ")[1]
                self.endpoints[k]["path_specs"] = re.sub(r'{[^}]*}*', '{}', k.split(" ")[1]).split("/")[1:]
                self.endpoints[k]["path_parameters"] = re.findall(r'{([^{}]+)}', k.split(" ")[1])
        for k, v in copy.deepcopy(self.endpoints).items(): # removed endpoints
            if k not in config["endpoints"].keys():
                del self.endpoints[k]
        for k1, v1 in config["endpoints"].items(): # updated endpoints
            for k2, v2 in v1.items():
                self.endpoints[k1][k2] = v2

        if update_pip_packages:
            with tempfile.TemporaryDirectory() as tempdir:
                with open(f"{tempdir}/requirements.txt", "w") as f:
                    for k, v in self.packages.items():
                        if v["source"] == "pip":
                            f.write(f"{k}=={v['version']}\n")
                execute(f"mkdir -p {tempdir}/packages")
                execute(f"pip3 install -t {tempdir}/packages -r {tempdir}/requirements.txt")
                for dir in os.listdir(f"{tempdir}/packages"):
                    if dir.endswith(".dist-info"):
                        dist_info = get_dist_info(f"{tempdir}/packages/{dir}")
                        for k, v in dist_info.items():
                            if k in self.packages.keys():
                                self.packages[k]["import"] = f"import {', '.join(v)}"
        if update_source_code:
            # updating modules
            for k1, v1 in self.modules.items():
                self.modules[k1]["source"] = "\n".join(
                    [v2["import"] for k2, v2 in self.tables.items()] +
                    [v2["import"] for k2, v2 in self.folders.items()] +
                    [v2["import"] for k2, v2 in self.packages.items()] +
                    [v2["import"] for k2, v2 in self.modules.items() if k1 != k2] +
                    [v1["content"]]
                )
            # updating endpoints
            for k1, v1 in self.endpoints.items():
                self.endpoints[k1]["source"] = "\n".join(
                    [v2["import"] for k2, v2 in self.tables.items()] +
                    [v2["import"] for k2, v2 in self.folders.items()] +
                    [v2["import"] for k2, v2 in self.packages.items()] +
                    [v2["import"] for k2, v2 in self.modules.items()] +
                    [v1["content"]]
                )

class Portfolio:
    def __init__(self, project_dir: str, template_dir: str):
        self.project_dir = project_dir
        self.template_dir = template_dir
        if not os.path.exists(self.project_dir):
            os.mkdir(self.project_dir)
    def create(self, name: str) -> None:
        s = Spinner("creating project...")
        shutil.copytree(self.template_dir, f"{self.project_dir}/{name}")
        project = Project()
        project.save(f"{self.project_dir}/{name}/state.yaml")
        s.stop("> project created")
    def delete(self, name: str) -> None:
        s = Spinner("deleting project...")
        shutil.rmtree(f"{self.project_dir}/{name}")
        s.stop("> project deleted")
    def activate(self, name: str, provider: str) -> None:
        login(provider)
        s = Spinner("initializing terraform...")
        execute(f"terraform -chdir={self.project_dir}/{name}/{provider} init")
        s.stop("> terraform initialized")
        s = Spinner("activating project...")
        execute(f"terraform -chdir={self.project_dir}/{name}/{provider} apply -auto-approve")
        s.stop("> project activated")
        print()
    def deactivate(self, name: str, provider: str) -> None:
        print()
        login(provider)
        print()
        s = Spinner("deactivating project...")
        execute(f"terraform -chdir={self.project_dir}/{name}/{provider} destroy -auto-approve")
        s.stop("> project deactivated")
        print()
    def push(self, name: str, path: str) -> None:
        print()
        spinner = Spinner("loading project...")
        project = Project()
        project.load(f"{self.project_dir}/{name}/state.yaml")
        spinner.stop("> project loaded")
        spinner = Spinner("updating project...")
        project.update(path)
        project.save(f"{self.project_dir}/{name}/state.yaml")
        spinner.stop("> project updated")
        print()
    def pull(self, name: str, path: str) -> None:
        project = Project()
        project.load(f"{self.project_dir}/{name}/state.yaml")
        with open(path, "w") as f:
            yaml.dump(project.config, f, default_flow_style=False, sort_keys=False)
    def list(self) -> list:
        if os.path.isdir(self.project_dir):
            return [dir for dir in os.listdir(self.project_dir)]
        else:
            return []
    def view(self, name: str) -> str:
        project = Project()
        project.load(f"{self.project_dir}/{name}/state.yaml")
        output = ""
        if project.config != {}:
            output = yaml.dump(project.config, default_flow_style=False)
        for provider in providers:
            if os.path.exists(f"{self.project_dir}/{name}/{provider}/url"):
                with open(f"{self.project_dir}/{name}/{provider}/url", "r") as f:
                    output += f"\n{provider}: {f.read().strip()}\n"
        return output