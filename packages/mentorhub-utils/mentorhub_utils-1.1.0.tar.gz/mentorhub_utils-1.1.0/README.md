# mentorHub-utils

PyPi install
```sh
pipenv install mentorhub-utils
```

## Overview
These utilities support the mentorHub platform. 

#### Table of Contents
- [Flask Utilities](#flask-utilities)
- [Config Utilities](#config-utilities)
- [Mongo Utilities](#mongo-utilities)
- [Contributing](#contributing)

# Flask Utilities
This is a collection of simple Flask utilities:
- MongoJSONEncoder converts ObjectID and datetime values to strings
- create_token() builds a Roles Based Access Control (RBAC) token
- create_breadcrumb(token) builds the breadcrumb used when updating the database

## Usage

### MongoJSONEncoder
 This is a helper class that allows the flask.json method to properly handle ObjectID and datetime values by converting them to strings.
```py
from flask import Flask
from mentorhub_utils import MongoJSONEncoder

# Initialize Flask App
app = Flask(__name__)
app.json = MongoJSONEncoder(app)

# In flask request handler
from flask import jsonify
print jsonify(dict)
```

### Tokens
 All API's will be secured with industry standard bearer tokens used to implement Role Based Access Control (RBAC). The create_token method will decode the token and extract claims for a user_id and roles, throwing an exception if the token is not found or not properly encoded. 
```json
{
    "user_id": "The users PersonID",
    "roles": ["Staff", "Mentor", "Member"]
}
```
Valid roles are listed in the mentorhub-mongodb repo's [enumerators file](https://github.com/agile-learning-institute/mentorHub-mongodb/blob/main/configurations/enumerators/enumerators.json) but the roles listed above are the only one's currently used in the mentorHub platform.

### Breadcrumbs
 All database collections include a lastModified "breadcrumb" property used to track changes over time. The breadcrumb has the following properties:
```json
{
        "atTime": "date-time the document was last modified",
        "byUser": "UserID claim from the access token",
        "fromIp": "IP Address the request originated at",  
        "correlationId": "A correlationID to use in logging"
}
```

### Example
Here is how these methods are used in a Flask Route Handler
```py
from mentorhub_utils import create_breadcrumb, create_token
token = create_token()
breadcrumb = create_breadcrumb(token)
MyService.doSomething(myData, ..., token, breadcrumb)
logger.info(f"Did Something completed successfully {breadcrumb.correlationId}")
```

# Config Utilities
This is collection of utilities to support API Configuration in a standard way
- Mentorhub_Config handles configuration values
- config_routes() is a Flask request handler

## Usage
Standard Config

### Config
Standard mental hub configuration values. Configurations are managed in a consistent way favoring file based configuration values, then environment, configuration values, and then default values. See the [Mentorhub_Config.py](./mentorhub_utils/config/MentorHub_Config.py) for details on the configuration values.

```py
config = Mentorhub_Config.get_instance()
print config.LOGGING_LEVEL
```

### config_routes()
 This is a simple flask request handler to be used to expose the config data on a config endpoint.
```py
from flask import Flask
app = Flask(__name__)
config_handler = create_config_routes()
app.register_blueprint(config_handler, url_prefix='/api/config')
```

# Mongo Utilities
Simple wrappers for MongoIO and a Config Initializer. 
- [get_instance()](#get_instance)
- [initialize()](#initialize)
- [configure(enumerators_key)](#configureenumerators_key)
- [disconnect](#disconnect)
- [get_documents](#get_documentscollection_name-match-project-order)
- [get_document](#get_documentcollection_name-string_id)
- [create_document](#create_documentcollection_name-document)
- [update_document](#update_documentcollection_name-_id-updates)
- [delete_document](#delete_documentcollection_name-string_id)

## Usage

### get_instance()
 Get a reference to the Singleton object
```py
mongo_io = MentorHubMongoIO.get_instance()
```

### configure(enumerators_key)
 This method will initialize the MongoIO singleton object, connect to the database, and update the Config.versions and Config.enumerators values. You should call this function when initializing the mongodb connection. This method takes as a parameter the primary collection name used to load enumerators. 
```py
mongo_io = Mentorhub_MongoIO.get_instance()
mongo_io.configure(config.MAIN_COLLECTION_NAME)
```

### disconnect()
 This Method will disconnect from the database in a graceful way. You should call this method when the server process is ending.
```py
mongo_io = MentorHubMongoIO.get_instance()
mongo_io.disconnect()
```

### get_documents(collection_name, match, project, order)
 This is a convenience method to get a list of documents based on Mongo Match, project, and sort order parameters. 
```py
match = {"name": {"$regex": query}}
order = [('name', ASCENDING)]
project = {"_id":1,"name":1}
documents = mentorhub_mongoIO.get_documents("COLLECTION_NAME", match, project, order)
```
### get_document(collection_name, string_id)
 This is a convenience method to get a single document based on ID
```py
document = mentorhub_mongoIO.get_document("COLLECTION_NAME", "_ID String")
```

### create_document(collection_name, document)
 This is a convenient method for creating a single document
```py
document = {"foo":"bar"}
created = mentorhub_mongoIO.create_document("COLLECTION_NAME", document)
```

### update_document(collection_name, _id, updates)
 This is a convenience method for updating a single document based on ID
```py
id = "24-byte-id"
patch = {"foo":"bar"}
updated = mentorhub_mongoIO.update_document("COLLECTION_NAME", id, patch)
```

### delete_document(collection_name, string_id)
 This is a convenience method for deleting a document based on ID. This is an actual live delete, not a soft delete. 
```py
id = "24-byte-id"
updated = mentorhub_mongoIO.delete_document("COLLECTION_NAME", id)
```

# Contributing
If you want to contribute to this library, here are the instructions.

## Prerequisites

- [Python](https://www.python.org/downloads/)
- [Pipenv](https://pipenv.pypa.io/en/latest/installation.html)

## Install Dependencies
```bash
pipenv install --dev
```

## Run unit testing
```bash
pipenv run unit
```

## Test setup.py package 
```bash
pipenv run test
```

## Clean package build path
```bash
pipenv run clean
```

### Build the Package
```bash
pipenv run build
```

## Twine check 
To check if the package is ready to publish
```bash
pipenv run check
```

# Publish the Package
You should successfully run ``clean``, ``build`` and ``check`` before publishing.
```bash
pipenv run publish
```
NOTE: You will be prompted for PyPi authentication credentials. You should not need to use the command, it is used by the GitHub Actions CI. 

