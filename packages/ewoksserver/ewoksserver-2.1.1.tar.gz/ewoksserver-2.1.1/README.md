# ewoksserver

ewoksserver is a REST server to manage and execute [ewoks](https://ewoks.readthedocs.io/) workflows.

It serves as a backend for [ewoksweb](https://ewoksweb.readthedocs.io/) and emits ewoks execution events over Socket.IO.

## Getting started

Install the [ewoksserver](https://ewoksserver.readthedocs.io/en/latest/) Python package

```
pip install ewoksserver
```

## Development

Install from source

```bash
pip install -e .[dev]
```

Run tests

```bash
pytest
```

Launch the backend

```bash
ewoks-server
```

or for an installation with the system python

```bash
python3 -m ewoksserver.server
```

## Configuration

The configuration keys are uppercase variables in a python script:

```python
# /tmp/config.py
RESOURCE_DIRECTORY = "/path/to/resource/directory/"

EWOKS_EXECUTION = {"handlers": ...}

CELERY = {"broker_url":...}
```

Specify the configuration file through the CLI

```bash
ewoks-server --config /tmp/config.py
```

or using the environment variable EWOKSSERVER_SETTINGS

```bash
export EWOKSSERVER_SETTINGS=/tmp/config.py
ewoks-server
```

### Example

```python
import os

_SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

RESOURCE_DIRECTORY = os.path.join(_SCRIPT_DIR, "resources")

EWOKS_EXECUTION = {
    "handlers": [
        {
            "class": "ewokscore.events.handlers.Sqlite3EwoksEventHandler",
            "arguments": [
                {
                    "name": "uri",
                    "value": "file:" + os.path.join(_SCRIPT_DIR, "ewoks_events.db"),
                }
            ],
        }
    ]
}
```

## Documentation

https://ewoksserver.readthedocs.io/
