# Introduction 
This project is a Python Client library for integrating with RPS Engine API for the sake of performing transformation to your data.

# Getting Started
**Pre requisites**
- Python version : >=3.10,<=3.11.9
- Install poetry for dependency management : https://python-poetry.org/docs/#installing-with-pipx
- **Enabled configuration** in RPS Core Admin website, filled with Transformation sequences, instances, rights and processing contexts.

*Disclaimer : This project was only tested with python 3.11*

## Starting the Application
The project uses poetry for dependency management and a pyproject.toml

To get started with poetry and you have pipx installed run
```bash
pipx install poetry 
```

Install the project dependencies (under the folder which contains the pyproject.toml)

```bash
poetry install
```

**Examples of usage**

The examples folder contains several ready-to-run scripts that demonstrate different usage scenarios of the RPS Engine client. Each example is designed to help you understand how to configure, invoke, and extend the client for your own use cases. Below is a brief explanation of each example:

- `simple_usage_example.py`
Demonstrates the most basic workflow: manually creating rights and processing contexts, constructing RPSValue objects, and performing protection and deprotection operations. This is a good starting point for understanding the core API and data flow.

- `contexts_provided_by_resolver_example.py`
Shows how to use context names instead of full context objects. The example leverages the context resolver to fetch rights and processing contexts by name, simplifying the request construction process.

- `usage_with_dependencies_example.py`
Illustrates how to handle RPSValue objects that have dependencies (such as minimum or maximum values). This is useful for scenarios where the transformation logic depends on related data fields.

- `usage_with_related_object_example.py`
Demonstrates how to load data from an external JSON file, convert it into RPSValue objects, and perform protection operations. This example is ideal for batch processing or integrating with external data sources.

**Each example is self-contained and can be run directly.** Review and adapt these scripts to accelerate your own integration with the RPS Platform.

```powershell
poetry run python client/examples/usage_with_related_object_example.py
```

# Configuration

The RPS Platform client supports flexible configuration through both `.env` file,  a `settings.json` file and environment variables. You can choose the method that best fits your deployment and development workflow.

The precedence order for loading configuration is : env -> settings.json 

**Supported Configuration Files**
- `.env` file: Use standard key-value pairs, one per line, with no quotes or commas, (e.g., KEY=value) for environment-based configuration (with __ as a nesting separator for env variables). The .env has to be located inside the main `Client` directory.
- `settings.json` file: Must be a valid JSON syntax for more complex or nested configuration. Using double quotes for all keys and string values, and proper nesting for objects and arrays. This is the recommended approach for most use cases.

**Choose how rights and processing contexts are loaded**

The client library gives you the option to select how to load the Rights and Processing Contexts, either by external JSON files or directly from the `settings.json`.

By default, the engine uses the JSON file-based context provider, which loads contexts from the full file paths specified under `external_source_files` in the configuration file.

If you want to load contexts directly from the rights_contexts and processing_contexts sections of your `settings.json`, you can switch to the Settings Context Provider. To do this, simply comment out the JSON file provider lines in `engine_factory.py` and uncomment the settings provider lines.


# Settings.json 
**Structure**

The settings.json file should be a valid JSON object with the following sections:

`rps`:
Contains core connection and authentication settings for the RPS Engine and Identity API.

- engineHostName (string): The base URL for the RPS Engine API.
- identityServiceHostName (string): The base URL for the Identity Service API.
- clientId (string): The client/application ID for authentication.
- clientSecret (string): The client/application secret for authentication.
- timeout (integer): Timeout in seconds for API requests.

`external_source_files` :
Specifies file paths for loading rights and processing contexts from external JSON files. Use absolute paths or paths relative to your project root.

- rightsContextsFilePath (string): Path to the rights contexts JSON file.
- processingContextsFilePath (string): Path to the processing contexts JSON file.

`rights_contexts` (optional):
Defines the rights contexts, according to the configuration in **RPS CoreAdmin**, with a list of evidences (name-value pairs) that describe the rights required for a transformation. 

```json
"rights_contexts": {
  "Admin": {
    "evidences": [
      { "name": "Role", "value": "Admin" }
    ]
  }
}
```

`processing_contexts` (optional):
Defines the processing contexts, according to the configuration in **RPS CoreAdmin**, with a list of evidences describing the processing actions (such as "Protect" or "Deprotect"). 

```json
"processing_contexts": {
  "Protect": {
    "evidences": [
      { "name": "Action", "value": "Protect" },
    ]
  },
  "Deprotect": {
    "evidences": [
      { "name": "Action", "value": "Deprotect" }
    ]
  }
}
```



# Contribute
To add libraries update the **dependencies** section in the ``pyproject.toml`` 

It is mandatory to use version pins for the dependency to ensure reproducible builds 
```toml
dependencies = [
    "pydantic (>=2.10.6,<3.0.0)",
    "pydantic-settings (>=2.8.1,<3.0.0)",
    "dotenv (>=0.9.9,<0.10.0)" ,
    "python-dotenv==1.0.0",
    "certifi==2023.7.22",
    "<INSERT YOUR DEPENDENCY>"
]
```

To install the dependencies update the peotry.lock with poetry
```
poetry lock
```
