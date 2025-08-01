
import os
from pathlib import Path

def json_filetree(parent_directory:str, keep_starter:bool = False):
    files = []
    for path in Path(parent_directory).rglob("*"):
        if not path.is_dir():
            # Convert path to string and remove the "endpoints/" prefix
            relative_path = str(path)
            if not keep_starter:
                relative_path.replace(parent_directory + "/", "", 1)
            files.append(relative_path)

    files_list = []
    for file in files:
        path = os.path.normpath(file)
        files_list.append(path.split(os.path.sep))

    result = {}

    # Process each path
    for path in files_list:
        current = result
        
        # Handle the last element (filename) separately
        *folders, filename = path
        
        # Navigate through the folders
        for folder in folders[:-1]:  # All folders except the last one
            if folder not in current:
                current[folder] = {}
            current = current[folder]
        
        # Handle the last folder
        last_folder = folders[-1]
        if last_folder not in current:
            current[last_folder] = {"files": []}
        
        # If we have more than one folder and the last one doesn't have a nested structure
        if len(folders) > 1 and "files" not in current[last_folder]:
            current[last_folder] = {"files": []}
        
        # Add the file to the appropriate list
        if "files" in current[last_folder]:
            current[last_folder]["files"].append(filename)
        else:
            if len(folders) > 1:
                if "subpath" not in current[last_folder]:
                    current[last_folder]["subpath"] = []
                current[last_folder]["subpath"].append(filename)
    return result