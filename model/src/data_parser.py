import json
import pathlib
from pathlib import Path


def parse_json_data(filepath: Path) -> list[float]:
    """Opens the .json file, 
    parses all floats from [data][y]
    and appends them to list of floats.

    Args:
        filepath (pathlib.Path): Any path to .json file

    Returns:
        list[float]: Parsed list of floats from data y column
    """
    meas_floats = []
    try:
        f = open(filepath)
        json_object = json.load(f)
        for i in json_object['data']['y']:
            meas_floats.append(i)
        f.close()
    except:
        print("Failed to open file to parse json data.")
    return meas_floats

def process_path(rootpath: str) -> list[Path]:
    """Parses all json files specified from root path

    Args:
        rootpath (str): example: "../data/"

    Returns:
        list[Path: str]: pathlib.Path
    """
    files = [f for f in pathlib.Path().glob(f"{rootpath}*.json")]
    print(f"Found {len(files)} .json files.")
    return files

def parse_label(filepath: Path):
    """Searches for known labels from filepath
    and returns the matched label.
    
    Args:
        filepath (pathlib.Path): Any path to .json file

    Returns:
        str: Label for the data
    """
    # follows correct order of dataset
    # so output labeling [1, 0, 0] would equal pes etc.
    if "pes" in filepath.name:
        this_label = "pes"
    elif "puuvilla" in filepath.name:
        this_label = "puuvilla"
    elif "villa" in filepath.name:
        this_label = "villa"
    else:
        this_label = "unknown"
    return this_label

def split_sample(filepath: Path):
    result = filepath.name.split("_")
    

def main():
    files = [f for f in pathlib.Path().glob("../data/*.json")]
    measurement = parse_json_data(files[0])
    label = parse_label(files[0])
    print(label)
    return

if __name__ == "__main__":
    main()
    