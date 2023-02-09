import contextlib
import subprocess

from simple_term_menu import TerminalMenu
from yaspin import yaspin

from .classes import Portfolio

project_dir = "/volumes/projects"
template_dir = "/templates"

tempfile_path = "/volumes/tempfile"

debug = False
def execute(command, hidden=True):
    if debug:
        print(command)
        return subprocess.run(command, shell=True)
    else:
        return subprocess.run(command, shell=True, capture_output=hidden)
def prompt(options, header, footer):
    terminal_menu = TerminalMenu(options,
        title = f"\n{header}\n",
        status_bar = f"\n{footer}\n",
        status_bar_style = ("fg_black",),
        menu_cursor_style = ("fg_black",),
        preview_command = "python3 /scripts/preview.py {}",
        preview_size = 1.0
    )
    menu_entry_index = terminal_menu.show()
    if menu_entry_index is None:
        exit()
    else:
        return options[menu_entry_index]

def create():
    portfolio = Portfolio(project_dir, template_dir)
    projects = portfolio.list()
    print()
    if projects != []:
        print("current projects:\n")
        for project in projects:
            print(f"  {project}")
        print()
    with contextlib.suppress(KeyboardInterrupt):
        name = input("enter project name: ")
        print()
        if name in projects:
            print("project already exists\n")
            return
        else:
            portfolio.create(name)
            print()
def delete():
    portfolio = Portfolio(project_dir, template_dir)
    projects = portfolio.list()
    if projects == []:
        print("\nno projects found\n")
        return
    project = prompt(projects, "select project to delete", "ctrl-c to cancel")
    print()
    portfolio.delete(project)
    print()
def push():
    portfolio = Portfolio(project_dir, template_dir)
    projects = portfolio.list()
    if projects == []:
        print("\nno projects found\n")
        return
    project = prompt(projects, "select project to push", "ctrl-c to cancel")
    portfolio.push(project, tempfile_path)
def pull():
    portfolio = Portfolio(project_dir, template_dir)
    projects = portfolio.list()
    if projects == []:
        print("\nno projects found\n")
        return
    project = prompt(projects, "select project to pull", "ctrl-c to cancel")
    portfolio.pull(project, tempfile_path)
def activate():
    portfolio = Portfolio(project_dir, template_dir)
    projects = portfolio.list()
    if projects == []:
        print("\nno projects found\n")
        return
    project = prompt(projects, "select project to activate", "ctrl-c to cancel")
    portfolio.activate(project, "aws")
def deactivate():
    portfolio = Portfolio(project_dir, template_dir)
    projects = portfolio.list()
    if projects == []:
        print("\nno projects found\n")
        return
    project = prompt(projects, "select project to deactivate", "ctrl-c to cancel")
    portfolio.deactivate(project, "aws")
def view():
    portfolio = Portfolio(project_dir, template_dir)
    projects = portfolio.list()
    if projects == []:
        print("\nno projects found\n")
        return
    project = prompt(projects, "select project to view", "ctrl-c to cancel")
    print()
    print(portfolio.view(project))