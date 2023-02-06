import boto3
import os
import shutil

s3 = boto3.client("s3")
required_packages = ["s3fs"]
installed_packages = []

def handler(event, context):
    global s3, required_packages, installed_packages
    current_packages = sorted(required_packages + list(set(installed_packages) - set(required_packages)))
    configured_packages = sorted(required_packages + list(set(event["packages"]) - set(required_packages)))
    if current_packages != configured_packages:
        os.makedirs("/tmp/packages/python", exist_ok=True)
        os.system(f"pip3 install {' '.join(configured_packages)} -t /tmp/packages/python")
        shutil.make_archive("/tmp/layer", "zip", "/tmp/packages")
        s3.upload_file("/tmp/layer.zip", event["bucket"], event["key"])
        installed_packages = sorted(event["packages"])
