# projgen/core.py
import os


def validate_entry(entry):
    name = entry["name"]
    level = entry["level"]
    entry_type = entry["type"]

    expected_level = name.count("/") + 1
    if level != expected_level:
        raise ValueError(
            f"Level mismatch in entry: '{name}'. Expected level {expected_level}, but got {level}."
        )
    extensionless_files = {"Dockerfile", "Makefile", "LICENSE", "README", "NOTICE"}

    if entry_type == "file":
        base_name = os.path.basename(name)
        if (
            not os.path.splitext(name)[1]
            and not base_name.startswith(".")
            and base_name not in extensionless_files
        ):
            raise ValueError(f"File '{name}' has no extension.")
    elif entry_type == "folder":
        if os.path.splitext(name)[1]:
            raise ValueError(f"Folder '{name}' should not have a file extension.")
    else:
        raise ValueError(f"Invalid type '{entry_type}' in entry: {name}")


def create_entry(base_path, entry):
    entry_path = os.path.join(base_path, entry["name"])
    if entry["type"] == "folder":
        os.makedirs(entry_path, exist_ok=True)
    else:
        dir_path = os.path.dirname(entry_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        with open(entry_path, "w") as f:
            f.write("")


def create_project_from_json(data):
    project_name = data.get("project_name")
    structure = data.get("project-structure", [])

    if not project_name:
        raise ValueError("Missing 'project_name' field.")

    original_name = project_name
    i = 1
    while os.path.exists(project_name):
        print(f"Project '{project_name}' already exists.")
        new_name = input(
            "Enter a new project name or press Enter to auto-generate: "
        ).strip()
        if new_name:
            project_name = new_name
        else:
            project_name = f"{original_name}-{i}"
            i += 1

    print(f"Creating project: {project_name}")
    os.makedirs(project_name)

    for entry in structure:
        validate_entry(entry)
        create_entry(project_name, entry)

    print(f"Project '{project_name}' created successfully.")
