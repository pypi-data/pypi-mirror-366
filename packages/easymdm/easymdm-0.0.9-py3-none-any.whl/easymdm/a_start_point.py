from easymdm.b_data_source import load_file_data
from easymdm.b_data_source import load_database_data
from easymdm.b_data_source import load_sqlite_data
from easymdm.c_blocking import process_blocking
from easymdm.d_similarity import process_similarity
from easymdm.e_priority_survivor import process_write_outputs
import yaml
import pandas as pd


def dispatcher(data_style, *args):
    if data_style == "file":
        if len(args) == 3:  # Expect file_name, config, and out_path
            file_name = args[0]  # args[0] is the file name
            config_path = args[1]  # args[1] is config file path
            out_path = args[2]
            df = load_file_data(file_name)  # Pass the actual file name
            # print(df)
            candidate_pairs = process_blocking(df, config_path) 
            features = process_similarity(df, config_path, candidate_pairs)
            process_write_outputs(df, features, config_path, out_path)
        else:
            raise ValueError(f"file data_style requires exactly 3 arguments (file_name, config, out_path), got {len(args)}: {args}")
    elif data_style == "sqlite":
        if len(args) == 3:  # Expect only table and config
            config_path = args[1]  # args[1] is config file path
            out_path = args[2]
            df = load_sqlite_data(args[0], args[1])  # Pass data_style explicitly
            # print(df)
            candidate_pairs = process_blocking(df, config_path) 
            features = process_similarity(df, config_path, candidate_pairs) 
            process_write_outputs(df, features, config_path, out_path)
        else:
            raise ValueError(f"sqlite data_style requires exactly 2 arguments (table, config), got {len(args)}: {args}")
    else:
        raise ValueError("Unknown data_style. Use 'file' or 'sqlite'.")
