import argparse
import yaml
from easymdm.a_start_point import dispatcher
# from easymdm.b_data_source import load_file_data
# from easymdm.b_data_source import load_database_data
# from easymdm.b_data_source import load_sqlite_data


def main():
    parser = argparse.ArgumentParser(description="CLI for mypackage")
    parser.add_argument('--source', choices=['file', 'database', 'sqlite'], required=True, help="Data source type")
    parser.add_argument('--name', help="File name (required if source is file)")
    parser.add_argument('--table', help="Schema and table name (required if source is database), e.g., schema.table")
    parser.add_argument('--config', default='config.yaml', help="Path to YAML config file")
    parser.add_argument('--outpath', default='out/', help="Output path for results")

    args = parser.parse_args()

    # Validate arguments based on source
    if args.source == 'file':
        if not args.name or not args.config or not args.outpath:
            parser.error("--name & --config  & --outpath are required when source is file")
        print(f"Loading data from file: {args.name}")
        # df = load_file_data(args.source, args.name)
        dispatcher(args.source, args.name, args.config, args.outpath)


        # df = load_file_data(args.name)

    elif args.source == 'database':
        if not args.table:
            parser.error("--table is required when source is database")
        # df = load_database_data(args.source, args.table)
        dispatcher(args.source, args.table)
    # elif args.source == 'sqlite':
    #     if not args.table:
    #         parser.error("--table is required when source is database")
    #     df = load_sqlite_data(args.table)
    elif args.source == 'sqlite':
        if not args.table or not args.config or not args.outpath:
            parser.error("--table & --config & --outpath are required : source = sqlite")
            sys.exit(1) 
        # df = load_sqlite_data(args.source, args.table, args.config)
        dispatcher(args.source, args.table, args.config, args.outpath)
        # sys.exit(0)
    # # Load YAML config
    # try:
    #     with open(args.config, 'r') as f:
    #         config = yaml.safe_load(f)
    # except FileNotFoundError:
    #     print(f"Error: Config file '{args.config}' not found.")
    #     return

    # # Process the DataFrame
    # result = process_dataframe(df, config)
    # print(result)  # Or handle the result as needed

if __name__ == '__main__':
    main()