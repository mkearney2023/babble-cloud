import sys
import simplejson as json
import importlib.util
import traceback

table_module = """
import boto3
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("table_id")
hash_key = table.key_schema[0]["AttributeName"]
class Module:
    def __len__(self):
        return len(table.scan()["Items"])
    def __getitem__(self, key):
        return table.get_item(Key = {hash_key: key})["Item"]["value"]
    def __setitem__(self, key, value):
        item = {
            hash_key: key,
            "value": value
        }
        table.put_item(Item = item)
    def __delitem__(self, key):
        table.delete_item(Key = {hash_key: key})
    def __iter__(self):
        return iter(table.scan()["Items"])
    def __contains__(self, key):
        item = table.get_item(Key = {hash_key: key}).get("Item")
        return item != None

    def put_item(self, item: dict):
        table.put_item(Item = item)
    def get_item(self, item: dict):
        return table.get_item(Key = {hash_key: item[hash_key]}).get("Item")
    def delete_item(self, item: dict):
        table.delete_item(Key = {hash_key: item[hash_key]})
    def scan(self):
        return table.scan()["Items"]
"""

folder_module = """
import s3fs

fs = s3fs.S3FileSystem(anon=False)
bucket = "folder_id"

class Module:
    def __init__(self):
        pass
    def open(self, file, mode):
        file = file.strip("/")
        return fs.open(f"{bucket}/{file}", mode)
    def url(self, file, expiration=3600):
        file = file.strip("/")
        return fs.url(f"{bucket}/{file}", expires=expiration)
"""

with open("state.json", "r") as f:
    state = json.load(f)

all_modules = {}
for k, v in state["tables"].items():
    all_modules[v["id"]] = table_module.replace("table_id", v["id"])
for k, v in state["folders"].items():
    all_modules[v["id"]] = folder_module.replace("folder_id", v["id"])
for k, v in state["modules"].items():
    all_modules[v["id"]] = v["source"]
for k, v in state["endpoints"].items():
    all_modules[v["id"]] = v["source"]

# BLANK MODULES (to prevent ModuleNotFoundError)
for k, v in all_modules.items():
    spec = importlib.util.spec_from_loader(k, loader=None)
    module = importlib.util.module_from_spec(spec)
    exec("", module.__dict__)
    sys.modules[k] = module
    globals()[k] = module
# MODULES WITH SOURCE CODE
for k, v in all_modules.items():
    spec = importlib.util.spec_from_loader(k, loader=None)
    module = importlib.util.module_from_spec(spec)
    exec(v, module.__dict__)
    sys.modules[k] = module
    globals()[k] = module

def get_output(method, headers, path, query, body):
    endpoint_id = ""
    path_parts = path.split("/")[1:]
    path_params = []
    path_specs = []
    for k, v in state["endpoints"].items():
        if v["method"] == method:
            if len(v["path_specs"]) == len(path_parts):
                match = True
                for path_spec, path_part in zip(v["path_specs"], path_parts):
                    if path_spec != path_part and path_spec != "{}":
                        match = False; break
                if match:
                    endpoint_id = v["id"]
                    path_params = v["path_parameters"]
                    path_specs = v["path_specs"]
                    break
    if endpoint_id == "":
        return {
            "statusCode": 404,
            "body": "Not Found"
        }
    else:
        path_parameters = {}
        for i in range(len(path_parts)):
            current_param = 0
            if path_specs[i] == "{}":
                path_parameters[path_params[current_param]] = path_parts[i]
                current_param += 1
        try:
            return {
                "statusCode": 200,
                "body": json.dumps(sys.modules[endpoint_id].request(headers, path_parameters, query, body), use_decimal = True)
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "body": str(traceback.format_exc())
            }

# HANDLER
def handler(event, context):
    return get_output(event["httpMethod"], event["headers"], event["path"], event["queryStringParameters"], event.get("body", ""))