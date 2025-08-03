import pandas as pd
import sqlite3
import yaml

def load_file_data(file_name):
    try:
        df = pd.read_csv(file_name)
        df.reset_index(drop=True, inplace=True)
        df.index.name = 'record_id'
        # print(df)
        return df
    except FileNotFoundError:
        raise ValueError(f"File '{file_name}' not found.")
    except Exception as e:
        raise ValueError(f"Error loading file: {str(e)}")

# work on this , by adding connectiovault here for other traditional rdbms
def load_database_data(schema_table):
    try:
        schema, table = schema_table.split('.')
        # Example pseudocode; replace with actual database connection
        # conn = some_database_library.connect()
        # query = f"SELECT * FROM {schema}.{table}"
        # df = pd.read_sql(query, conn)
        df = pd.DataFrame({'example': [1, 2, 3]})  # Placeholder
        df.reset_index(drop=True, inplace=True)
        df.index.name = 'record_id'
        print(df)
        return df
    except ValueError:
        raise ValueError("Table must be in 'schema.table' format.")
    except Exception as e:
        raise ValueError(f"Error loading database: {str(e)}")


def load_sqlite_data(schema_table, yaml_path):
    try:
        # Load DB config from YAML file
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)

        # Access first item in the 'sqlite' list
        sqlite_cfg = config['sqlite'][0]
        DB_PATH = sqlite_cfg['DB_PATH']
        DB_NAME = sqlite_cfg['DB_NAME']

        # Connect to the database
        schema, table = schema_table.split('.')
        FULL_DB_PATH = f"{DB_PATH}{DB_NAME}"
        conn = sqlite3.connect(FULL_DB_PATH)
        df = pd.read_sql_query(f"SELECT * FROM {schema}.{table}", conn)
        df.reset_index(drop=True, inplace=True)
        df.index.name = 'record_id'
        # print(df)
        conn.close()
        return df

    except ValueError:
        raise ValueError("Table must be in 'schema.table' format.")
    except Exception as e:
        raise ValueError(f"Error loading SQLite data: {str(e)}")


if __name__ == '__main__':
    load_file_data()
    load_database_data('sche.table')
