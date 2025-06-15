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
    exclude = validate_sample_meas_count(files)
    num_excluded = 0
    fixed_files = []
    for i in files:
        flag = False
        for j in exclude:
            if j in i.name:
                print(i.name)
                num_excluded += 1
                flag = True
        
        if not flag:
            fixed_files.append(i)
            
    print(f"Excluded {num_excluded} files and returning {len(fixed_files)}/{len(files)} files")
    return fixed_files

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

def validate_sample_meas_count(files: list[Path]) -> list[str]:
    """
    Searches for extra entries or missing entries.
    Uses material type, index and measurement index to
    ensure resulting list of data only contains full 10 measurement
    entries

    Args:
    files: List of paths to parse

    Returns:
    A list of strings which match a filepath that should be excluded from
    dataset due to missing entries or being an extra entry
    """
    # First split the filename by _ to get fabric type, material index, sensor index 
    # sensor index is opt, because first index file is not notated by _index)
    not_found_amnt = 0
    extra_entries = 0
    exclude = []
    
    found_pes = 0
    found_cotton = 0
    found_wool = 0
    pes_indices = []
    cotton_indices = []
    wool_indices = []
    
    
    for filepath in files:
        result = filepath.name.split("_")
        if result.__len__() == 2:
            # this is the first sensor (1) that took the measurement
            mat_index = result[1]
            # Because mat index has the .json split in it we get rid of it
            mat_index = result[1].split(".json")[0]
            fab_type = result[0]
            
            if "pes" in filepath.name:
                found_pes += 1
                pes_indices.append(mat_index)
            elif "puuvilla" in filepath.name:
                found_cotton += 1
                cotton_indices.append(mat_index)
            elif "villa" in filepath.name:
                found_wool += 1
                wool_indices.append(mat_index)
                
                
            # Ensure, that we have an existing sensor indexes 2-10 as files
            i = 1
            while i <= 11:
                if (pathlib.Path.exists(pathlib.Path(f"../data/{fab_type}_{mat_index}_{i}.json"))):
                    if i == 11:
                        print(f"{fab_type} index {mat_index} meas {i} found extra: {i}")
                        extra_entries += 1
                        exclude.append(f"{fab_type}_{mat_index}_{i}.json") 
                    elif i == 1:
                        print(f"{fab_type} index {mat_index} meas {i} found extra: {i}")
                        extra_entries += 1
                        exclude.append(f"{fab_type}_{mat_index}_{i}.json")
                    pass
                else:
                    if i != 11 and i != 1:
                        print(f"{fab_type} index {mat_index} meas {i} does not exist")
                        not_found_amnt += 1
                        exclude.append(f"{fab_type}_{mat_index}")
                i += 1
    
    print(f"Polyester samples found: {found_pes}")
    print(f"Cotton samples found: {found_cotton}")
    print(f"Wool samples found: {found_wool}")
    
    root_indices = { "pes": pes_indices, 
                    "puuvilla": cotton_indices, 
                    "villa": wool_indices
                    }
    
    # Search again for missing root indices
    missing_roots = []
    for filepath in files:
        result = filepath.name.split("_")
        if result.__len__() == 3:
            mat_index = result[1]
            # If already found missing root index for material go next
            if missing_roots.count(mat_index) == 1:
                continue
            
            fab_type = result[0]
            li = root_indices.get(fab_type)
            if li != None and li.count(mat_index) == 0:
                print(f"Missing first meas: {fab_type} {mat_index}")
                missing_roots.append(mat_index)
                exclude.append(f"{fab_type}_{mat_index}")
                not_found_amnt += 1
    
    print(f"Validated {files.__len__()} files, found {not_found_amnt} missing entries and extra entries {extra_entries}.")
    #print(f"Item names excluded from dataset (match): \n {exclude}")
    return exclude

def main():
    files = [f for f in pathlib.Path().glob("../data/*.json")]
    validate_sample_meas_count(files)
    #measurement = parse_json_data(files[0])
    #label = parse_label(files[0])
    #print(label)
    return

if __name__ == "__main__":
    main()
    