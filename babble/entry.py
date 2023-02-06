import argparse
import pathlib
import subprocess
import shutil
import os

from simple_term_menu import TerminalMenu

path = f"{pathlib.Path(__file__).parent.absolute()}"

if not os.path.exists(f"{path}/projects"):
    os.mkdir(f"{path}/projects")

def prompt(options, header, footer):
    terminal_menu = TerminalMenu(options,
        title = f"\n{header}\n",
        status_bar = f"\n{footer}\n",
        status_bar_style = ("fg_black",),
        menu_cursor_style = ("fg_black",),
        preview_command = f"cat {path}/projects/{{}}/config.yaml",
        preview_size = 1.0
    )
    menu_entry_index = terminal_menu.show()
    if menu_entry_index is None:
        exit()
    else:
        return options[menu_entry_index]

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

projects = os.listdir(f"{path}/projects")

args = parser.parse_args()
volume = f"{path}/projects"

if not args.action == "help":
    check_if_docker_installed = subprocess.run("docker --version", shell=True, capture_output=True)
    if check_if_docker_installed.returncode != 0:
        print("\nERROR: Please install docker and try again.\n")
        exit()
    check_if_built = subprocess.run("docker image inspect babble-cloud", shell=True, capture_output=True)
    if check_if_built.returncode != 0:
        exit()
    build_image = subprocess.run(f"docker build -t babble-cloud {path}", shell=True)
    if build_image.returncode != 0:
        exit()

def main():
    if args.action == "create":
        os.system(f"docker run --rm -v {volume}:/projects -it babble-cloud create")
    elif args.action == "delete":
        os.system(f"docker run --rm -v {volume}:/projects -it babble-cloud delete")
    elif args.action == "activate":
        os.system(f"docker run --rm -v {volume}:/projects -it babble-cloud activate")
    elif args.action == "deactivate":
        os.system(f"docker run --rm -v {volume}:/projects -it babble-cloud deactivate")
    elif args.action == "view":
        os.system(f"docker run --rm -v {volume}:/projects -it babble-cloud view")
    elif args.action == "push":
        if len(projects) == 0:
            print("\n> no projects found\n")
            exit()
        project = prompt(projects, "select a project", "ctrl-c to cancel")
        shutil.copy(args.file, f"{path}/projects/{project}/config.yaml")
        print()
    elif args.action == "pull":
        if len(projects) == 0:
            print("\n> no projects found\n")
            exit()
        project = prompt(projects, "select a project", "ctrl-c to cancel")
        shutil.copy(f"{path}/projects/{project}/config.yaml", args.file)
        print()