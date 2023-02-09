import argparse
import pathlib
import os
import subprocess

file_path = pathlib.Path(__file__).parent.absolute()

image_name = "babble-cloud"
volumes = f"{file_path}/volumes"
tempfile_path = f"{file_path}/volumes/tempfile"
dockerfile_path = file_path

def docker_is_installed() -> bool:
    result = subprocess.run("docker --version", shell=True, capture_output=True)
    return result.returncode == 0
def image_is_built() -> bool:
    result = subprocess.run(f"docker image inspect {image_name}", shell=True, capture_output=True)
    return result.returncode == 0
def build_image() -> bool:
    result = subprocess.run(f"docker build -t {image_name} {dockerfile_path}", shell=True)
    return result.returncode == 0

if not docker_is_installed():
    print("ERROR: check your docker installation and try again")
    exit(-1)
if not image_is_built():
    success = build_image()
    if not success:
        exit(-1)

parser = argparse.ArgumentParser()
action = parser.add_subparsers(dest = "action")

create = action.add_parser("create")
delete = action.add_parser("delete")
activate = action.add_parser("activate")
deactivate = action.add_parser("deactivate")
view = action.add_parser("view")
push = action.add_parser("push")
push.add_argument("file")
pull = action.add_parser("pull")
pull.add_argument("file")

args = parser.parse_args()

def main():
    if args.action == "create":
        os.system(f"docker run --rm -v {volumes}:/volumes -it babble-cloud create")
    elif args.action == "delete":
        os.system(f"docker run --rm -v {volumes}:/volumes -it babble-cloud delete")
    elif args.action == "activate":
        os.system(f"docker run --rm -v {volumes}:/volumes -it babble-cloud activate")
    elif args.action == "deactivate":
        os.system(f"docker run --rm -v {volumes}:/volumes -it babble-cloud deactivate")
    elif args.action == "view":
        os.system(f"docker run --rm -v {volumes}:/volumes -it babble-cloud view")
    elif args.action == "push":
        with open(args.file, "r") as f:
            content = f.read()
        with open(tempfile_path, "w") as f:
            f.write(content)
        os.system(f"docker run --rm -v {volumes}:/volumes -it babble-cloud push")
        os.remove(tempfile_path)
    elif args.action == "pull":
        os.system(f"docker run --rm -v {volumes}:/volumes -it babble-cloud pull")
        with open(tempfile_path, "r") as f:
            content = f.read()
        with open(args.file, "w") as f:
            f.write(content)
        os.remove(tempfile_path)