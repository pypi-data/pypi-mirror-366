from data_save import save_data, storage_file_exists
from config_loader import load_config, get_path, get_setting, change_path
import numpy as np # type: ignore


change_path("storage_dir", "storage")