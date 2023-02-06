import subprocess
import os

from simple_term_menu import TerminalMenu

def prompt(options, header, footer):
    terminal_menu = TerminalMenu(options,
        title = f"\n{header}\n",
        status_bar = f"\n{footer}\n",
        status_bar_style = ("fg_black",),
        menu_cursor_style = ("fg_black",),
        preview_command = "cat /projects/{}/config.yaml",
        preview_size = 1.0
    )
    menu_entry_index = terminal_menu.show()
    if menu_entry_index is None:
        exit()
    else:
        return options[menu_entry_index]
def execute(command):
    result = subprocess.run(command, shell=True, capture_output=True)
    return {
        "code": result.returncode,
        "output": str(result.stdout, "utf-8"),
    }
def table(dicts, keys = [], headers = []):
    if dicts == []: return ''
    if keys == []:
        for dict in dicts:
            for key in dict:
                if key not in keys:
                    keys.append(key)
    if len(headers) != len(keys):
        headers = keys.copy()
    widths = [len(header) for header in headers]
    for i in range(len(keys)):
        for dict in dicts:
            if keys[i] in dict:
                if len(str(dict[keys[i]])) > widths[i]:
                    widths[i] = len(str(dict[keys[i]]))
    output = '\n┌'
    for i in range(len(headers)):
        output += '─' * (widths[i] + 2) + '┬'
    output = output[:-1] + '┐\n'
    for i in range(len(headers)):
        output += '│ ' + headers[i].ljust(widths[i]) + ' '
    output += '│\n├'
    for i in range(len(headers)):
        output += '─' * (widths[i] + 2) + '┼'
    output = output[:-1] + '┤\n'
    for dict in dicts:
        for i in range(len(headers)):
            output += '│ ' + str(dict[keys[i]]).ljust(widths[i]) + ' '
        output += '│\n'
    output += '└'
    for i in range(len(headers)):
        output += '─' * (widths[i] + 2) + '┴'
    output = output[:-1] + '┘\n'
    return output

def is_logged_in(provider):
    if provider == "aws":
        return execute("aws sts get-caller-identity")["code"] == 0
    elif provider == "azure":
        return execute("az account show")["code"] == 0
def login(provider):
    if provider == "aws":
        os.system("aws configure")
    elif provider == "azure":
        os.system("az login")
    elif provider == "gcp":
        os.system("gcloud init")
        project = util.execute("gcloud config get project")["output"].strip()
        service_account = ''.join(random.choice(string.ascii_lowercase) for i in range(30))
        os.system(f"gcloud iam service-accounts create {service_account}")
        os.system(f"gcloud iam service-accounts keys create /volume/gcp_credentials.json --iam-account={service_account}@{project}.iam.gserviceaccount.com")
        os.system(f"gcloud projects add-iam-policy-binding {project} --member serviceAccount:{service_account}@{project}.iam.gserviceaccount.com --role roles/viewer")
        os.system(f"gcloud projects add-iam-policy-binding {project} --member serviceAccount:{service_account}@{project}.iam.gserviceaccount.com --role roles/storage.admin")
        os.system("gcloud services enable cloudresourcemanager.googleapis.com")
        os.system("gcloud services enable cloudbilling.googleapis.com")
        os.system("gcloud services enable iam.googleapis.com")
        os.system("gcloud services enable storage.googleapis.com")
        os.system("gcloud services enable serviceusage.googleapis.com")

def project_list():
    return sorted(os.listdir("/projects"))
