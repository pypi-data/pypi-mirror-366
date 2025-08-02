

# projgen/cli.py
import argparse
import json
from projgen.core import create_project_from_json

def main():
    parser = argparse.ArgumentParser(description="📁 Generate project structure from JSON file.")
    parser.add_argument("json_file", help="Path to JSON structure file")
    args = parser.parse_args()

    with open(args.json_file, "r") as f:
        data = json.load(f)

    create_project_from_json(data)
