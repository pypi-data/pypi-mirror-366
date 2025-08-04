import os
import sys
import json
import argparse
from .app import create_app


def save(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(description="Save Redoc specs for EwoksServer")
    parser.add_argument(
        "filename",
        help="JSON filename in which to save the specs",
    )
    args = parser.parse_args(argv[1:])

    app = create_app()
    directory = os.path.dirname(args.filename)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(args.filename, "w") as fd:
        json.dump(app.openapi(), fd)


if __name__ == "__main__":
    sys.exit(save())
