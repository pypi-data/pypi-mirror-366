


# ProjGen 🛠️

A CLI tool to generate directory and file structures from a JSON file.

## Install

```bash
pip install projgen
```
## Usage
```bash
projgen path/to/project-structure.json
```
- Enter the project_name, it is optional

## Write the project structure in project-structure.json - A example below
```json
{
  "project_name": "my-fastapi-app",
  "project-structure": [
    { "level": 1, "type": "folder", "name": "app" },
    { "level": 2, "type": "file", "name": "app/main.py" },
    { "level": 2, "type": "folder", "name": "app/utils" },
    { "level": 1, "type": "file", "name": "README.md" },
    { "level": 1, "type": "file", "name": ".gitignore" }
  ]
}
```
## To run this clone project use this 
```bash
# build first using pip
pip install .
# then
projgen path_to_file.json
```

