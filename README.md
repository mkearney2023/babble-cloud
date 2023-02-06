
# Babble Cloud

Babble is a tool that enables beginner programmers to rapidly deploy serverless HTTP APIs to AWS through a low-code Pythonic YAML configuration file.


## Table of Contents

[Requirements](#requirements)  
[Installation](#installation)  
[Usage](#usage)  
[Configuration](#configuration)  
[Demonstration](#demonstration)
## Requirements

[Python](https://www.python.org/downloads/)  
[Docker](https://docs.docker.com/engine/install/)  
[AWS](https://aws.amazon.com/free/)

## Installation

To install Babble, run the following command:
```bash
  pip install babble-cloud
```
    
## Usage

To start a new project, run the following command:
```bash
  babble create
```
To set the configuration file for a project, run the following command:
```bash
  babble push <source file>
```
To retrieve the configuration file from a project, run the following command:
```bash
  babble pull <destination file>
```
To view the current configuration of a project, run the following command:
```bash
  babble view
```
To activate a project, run the following command:
```bash
  babble activate
```
To deactivate your project, run the following command:
```bash
  babble deactivate
```
To delete your project, run the following command:
```bash
  babble delete
```
**Note:**&nbsp; Upon running the commands `babble activate`, `babble deactivate`, and in some cases `babble delete`, you will be prompted for your AWS account credentials in order to add or remove the necessary resources from your AWS account.  For information about obtaining these credentials, please refer to the [AWS documentation](https://docs.aws.amazon.com/singlesignon/latest/userguide/howtogetcredentials.html) on getting IAM role credentials.
## Configuration

To configure your application infrastructure, you will need to create a YAML configuration file containing your resources.  Currently, resources fall under five categories: `tables`, `folders`, `packages`, `modules`, and `endpoints`.

### Tables
Table definitions are used to deploy DynamoDB tables to the user's AWS account.  The following methods can be accessed via dot notation from module and endpoint source code:

**`put_item(item: dict)`** - Creates a new item in the table, or replaces an old item with a new item.  It is required that the item contains the "key" attribute specified in the table's configuration. If an item that has the same "key" attribute as the new item already exists in the table, the new item completely replaces the existing item. Otherwise, an entirely new item will be created.

**`get_item(item: dict)`** - Retrieves an item from the table.  It is required that the item contains the "key" attribute specified in the table's configuration.  If there is no matching item, get_item will return an empty dict.

**`delete_item(item: dict)`** - Retrieves an item from the table.  It is required that the item contains the "key" attribute specified in the table's configuration.

**`scan()`** - Performs a full table scan, returning a list of all items in the table.

```yaml
tables:
    <table name>:
        key: <key name>
    <table name>:
        key: <key name>
    ...
```
### Folders
Folder definitions are used to deploy S3 buckets to the user's AWS account.  The following methods can be accessed via dot notation from module and endpoint source code:

**`open(path: str, mode: str)`** - Opens or creates an S3 file based on the `path` specification, and returns it as a file object. This method emulates the behavior of the standard Python `open` function.

**`url(path: str, expiration: int = 3600)`** - Returns a temporary download URL for an S3 file. This URL will be valid for the number of seconds specified by `expiration`, with a default value of 3600 seconds, or one hour.


```yaml
folders:
    <folder name>:
    <folder name>:
    ...
```
### Packages
Package definitions are used to include external packages in both module and endpoint source code.  These packages can be sourced from the Python Standard Library (lib), or from the Python Package Index (pip).
```yaml
packages:
    <package name>:
        source: <lib or pip>
        version: <version number or "~">
    <package name>:
        source: <lib or pip>
        version: <version number or "~">
    ...
```
### Modules
Module definitions are used to write source code for the application.  All functions, classes, and variables defined within these modules can be accessed via dot notation from module and endpoint source code. Please note that all imports are handled implicitly and there is no need for any import statements.  All tables, folders, packages, and other modules can be accessed via dot notation.
```yaml
modules:
    <module name>:
        content: |
            # source code goes here
    <module name>:
        content: |
            # source code goes here
    ...
```
### Endpoints
Endpoint definitions are used to write source code that processes the request data and determines the response data. Please note that all imports are handled implicitly and there is no need for any import statements.  All tables, folders, packages, and modules can be accessed via dot notation. It is imperative that all endpoints contain a function named `request` with the parameters `headers`, `path`, `query`, and `body` as shown below.
```yaml
endpoints:
    <endpoint method> <endpoint path>:
        content: |
            def request(headers, path, query, body):
                # source code goes here
                return response
    <endpoint method> <endpoint path>:
        content: |
            def request(headers, path, query, body):
                # source code goes here
                return response
```
## Demonstration

### Creation and Activation

**Step 1:**  Create a new project. Upon running this command, you will be prompted for a name for your new project.
```bash
babble create
```
**Step 2:**  Push your YAML configuration file to the project.  Upon running this command, you will be prompted to select a project you previously created.
```bash
babble push <filename>
```
**Step 3:**  Activate your project.  Upon running this command, you will be prompted to select a project you previously created.
```bash
babble activate
```
**Step 4:**  Obtain the URL for your newly created HTTP API.  Upon running this command, you will be prompted to select a project you previously created.
```bash
babble view
```

### Deactivation and Deletion
**Step 1:**  Deactivate your project.   Upon running this command, you will be prompted to select a project you previously created.
```bash
babble deactivate
```
**Step 2:**  Delete your project.   Upon running this command, you will be prompted to select a project you previously created.  If the selected project is not deactivated, it will be deactivated automatically.
```bash
babble delete
```

### Configuration File
Below is an example of a configuration file that can be used with Babble to deploy a serverless HTTP API with the following endpoints:

**`PUT /items/{item_id}`** - Creates a new entry in `my_table`, using the path parameter `item_id` as the key, and the JSON-formatted body for all other attributes.

**`GET /items/{item_id}`** - Returns an entry from `my_table`, using the path parameter `item_id` to find the entry.

**`DELETE /items/{item_id}`** - Deletes an entry from `my_table`, using the path parameter `item_id` to find the entry.

**`GET /items`** - Reads all entries in `my_table`, creates a Pandas DataFrame containing these entries, writes the DataFrame to the file `output.txt` in `my_folder`, and returns a temporary download URL for the newly created file.


```yaml
tables:
  my_table:
    key: my_key
folders:
  my_folder:
packages:
  pandas:
    source: pip
    version: 1.5.3
  json:
    source: lib
    version: ~
modules:
  my_module:
    content: |
      def get_item(item_key):
        return my_table.get_item({"my_key": item_key})
      def put_item(item_key, body):
        item = json.loads(body)
        item["my_key"] = item_key
        my_table.put_item(item)
      def delete_item(item_key):
        my_table.delete_item({"my_key": item_key})
      def get_items():
        items = my_table.scan()
        df = pandas.DataFrame.from_dict(items)
        with my_folder.open("output.txt", "w") as fp:
          fp.write(df.to_string())
        return my_folder.url("output.txt")
endpoints:
  GET /items/{item_key}:
    content: |
      def request(headers, path, query, body):
        return my_module.get_item(path["item_key"])
  PUT /items/{item_key}:
    content: |
      def request(headers, path, query, body):
        return my_module.put_item(path["item_key"], body)
  DELETE /items/{item_key}:
    content: |
      def request(headers, path, query, body):
        return my_module.delete_item(path["item_key"])
  GET /items:
    content: |
      def request(headers, path, query, body):
        return my_module.get_items()
```

