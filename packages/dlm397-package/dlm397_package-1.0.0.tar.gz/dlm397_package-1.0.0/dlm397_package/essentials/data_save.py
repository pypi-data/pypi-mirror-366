from config_loader import load_config, get_path, get_setting, get_home_path
import numpy as np # type: ignore
import os

def storage_file_exists():
    home_dir = get_home_path()
    storage_path = get_path("storage_dir")
    storage_dir = os.path.join(home_dir, storage_path)
    data_path = get_path("data_dir")
    data_dir = os.path.join(storage_dir, data_path)
    if os.path.exists(data_dir):
        return True
    elif not os.path.exists(storage_dir):
        i = input(f"file {storage_dir} does not exists, would you like to create one (y/n)?")
        if i == "y":
            os.mkdir(storage_dir)
        else:
            print("Exitting...")
            return False
    if os.path.exists(storage_dir) and not os.path.exists(data_dir):
        j = input(f"Directory {data_dir} does not exist, would you like to create it (y/n)?")
        if j == "y":
            os.mkdir(data_dir)
            return True
        else:
            print("Exitting...")
            return False

def save_data(data, file_name, path_key="data_dir"):
    if not storage_file_exists():
        return
    save_location = get_path(path_key)
    save_type = get_setting("default_format")
    data_type = str(type(data))
    if data_type == "<class 'numpy.ndarray'>":
        np.savetxt(f"{save_location}\\{file_name}.{save_type}", data, delimiter=',')
        return (f"{save_location}\\{file_name}.{save_type}")
    elif data_type == "<class 'list'>":
        np.savetxt(f"{save_location}\\{file_name}.{save_type}", data, delimiter=',')
        return (f"{save_location}\\{file_name}.{save_type}")
    else:
        print(f"failed, file type {data_type},not acceptable file type indentified.")
        return 
    
    