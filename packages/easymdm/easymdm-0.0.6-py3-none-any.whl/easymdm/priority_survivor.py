import networkx as nx
import yaml
import pandas as pd
from datetime import datetime

pd.set_option('future.no_silent_downcasting', True)


# 6. Apply priority survivorship rule
def apply_priority_rule(df, record_ids, priority_conditions):
    records = [df.loc[rid] for rid in record_ids]
    
    # Convert priority columns to match expected value type
    for condition in priority_conditions:
        column = condition['column']
        expected_value = condition['value']
        
        # Skip conversion if column doesn't exist
        if column not in df.columns:
            continue
            
        # Handle numeric or string values, but be more careful about conversion
        try:
            # Only convert if the column contains values that can be converted
            # Check if all non-null values are numeric-like
            non_null_values = df[column].dropna().astype(str)
            
            # Check if values look like they should be converted to the expected type
            if isinstance(expected_value, int):
                # Only convert if values look like integers (not dates)
                convertible_values = []
                for val in non_null_values:
                    # Skip date-like patterns
                    if '/' in str(val) or '-' in str(val) and len(str(val)) > 4:
                        continue
                    try:
                        int(val)
                        convertible_values.append(val)
                    except ValueError:
                        continue
                
                # Only proceed with conversion if we have convertible values
                if convertible_values:
                    df[column] = df[column].astype(str).replace(
                        {'0': 0, '1': 1, '0.0': 0, '1.0': 1, str(expected_value): expected_value}
                    )
                    # Convert only the convertible values
                    mask = df[column].astype(str).isin(['0', '1', '0.0', '1.0', str(expected_value)])
                    df.loc[mask, column] = df.loc[mask, column].astype(type(expected_value))
            
        except (ValueError, TypeError) as e:
            # Silently continue if conversion fails - this is expected for some columns
            continue
    
    # Check each condition in order
    for condition in priority_conditions:
        column = condition['column']
        expected_value = condition['value']
        
        if column not in df.columns:
            continue
            
        values = [rec[column] for rec in records]
        if values.count(expected_value) == 1:
            return record_ids[values.index(expected_value)]
    
    return None


# print("Clusters (auto_merge and unmatched only):", [list(cluster) for cluster in clusters])

# # 8. Create golden record for each cluster
# def create_golden_record(df, record_ids, survivorship_rules, priority_conditions):
#     trusted_id = apply_priority_rule(df, record_ids, priority_conditions) if len(record_ids) > 1 else record_ids[0]
#     golden = {}
    
#     if trusted_id:
#         golden = df.loc[trusted_id].to_dict()
#     else:
#         for column in df.columns:
#             if column in survivorship_rules:
#                 strategy = survivorship_rules[column]
#                 values = [df.loc[rid][column] for rid in record_ids]
#                 if strategy == 'most_common':
#                     most_common = Counter([v for v in values if pd.notna(v)]).most_common(1)
#                     golden[column] = most_common[0][0] if most_common else None
#                 elif strategy == 'longest_if_null':
#                     non_null_values = [v for v in values if pd.notna(v)]
#                     if non_null_values:
#                         most_common = Counter(non_null_values).most_common(1)
#                         golden[column] = most_common[0][0] if most_common else None
#                     else:
#                         # Fall back to longest string from all records
#                         all_values = []
#                         for rid in record_ids:
#                             val = df.loc[rid][column]
#                             all_values.append((val, len(str(val)) if pd.notna(val) else 0))
#                         if all_values:
#                             max_len_val = max(all_values, key=lambda x: x[1])[0]
#                             golden[column] = max_len_val if pd.notna(max_len_val) else None
#                         else:
#                             golden[column] = None
#                 elif strategy == 'most_recent':
#                     dates = [pd.to_datetime(df.loc[rid]['_load_datetime']) if '_load_datetime' in df.columns else pd.Timestamp.min for rid in record_ids]
#                     max_date_idx = dates.index(max(dates))
#                     golden[column] = values[max_date_idx]
#                 else:
#                     golden[column] = values[0]
#             else:
#                 golden[column] = df.loc[record_ids[0]][column]
#     return golden, trusted_id

def create_golden_record(df, record_ids, survivorship_rules, priority_conditions):
    trusted_id = apply_priority_rule(df, record_ids, priority_conditions) if len(record_ids) > 1 else record_ids[0]
    golden = {}
    
    # Get the date column from survivorship_rules where strategy is 'most_recent'
    date_column = next((col for col, strategy in survivorship_rules.items() if strategy == 'most_recent'), None)
    
    if trusted_id:
        return df.loc[trusted_id].to_dict(), trusted_id
    
    for column in df.columns:
        values = [df.loc[rid][column] for rid in record_ids]
        non_null_values = [v for v in values if pd.notna(v)]
        
        if non_null_values:
            if date_column and column.lower() == date_column.lower():
                dates = [pd.to_datetime(df.loc[rid][column]) if pd.notna(df.loc[rid][column]) else pd.Timestamp.min for rid in record_ids]
                max_date_idx = dates.index(max(dates))
                golden[column] = values[max_date_idx]
            else:
                golden[column] = non_null_values[0]
        else:
            golden[column] = None
            
    return golden, trusted_id


# 9. Write pairwise summary
def write_pairwise_summary(df, features, category, out_path, priority_rule):
    subset = features[features['match_category'] == category].reset_index()
    if subset.empty:
        # print(f"No pairs found for category: {category}")
        with open(out_path, 'a', encoding='utf-8') as f:
            f.write(f'\n--- {category.upper()} RECORDS ---\n')
            f.write(f"No {category} pairs found.\n")
            f.write('-' * 80 + '\n')
        return
    # The MultiIndex columns are named 'first' and 'second' after reset_index()
    subset[['id_min', 'id_max']] = subset[['first', 'second']].apply(sorted, axis=1, result_type='expand')
    subset = subset.drop_duplicates(subset=['id_min', 'id_max'])
    with open(out_path, 'a', encoding='utf-8') as f:
        f.write(f'\n--- {category.upper()} RECORDS ---\n')
        for _, row in subset.iterrows():
            id1, id2 = row['first'], row['second']
            trusted_id = apply_priority_rule(df, [id1, id2], priority_rule['conditions'])
            trusted_status = f"Trusted Record: {trusted_id}" if trusted_id else "Trusted Record: None (no priority match)"
            f.write(f"🔹 Record 1 ({id1}): {df.loc[id1].to_dict()}\n")
            f.write(f"🔸 Record 2 ({id2}): {df.loc[id2].to_dict()}\n")
            f.write(f"💡 Similarity Score: {round(row['score'], 4)} | Match Category: {category}\n")
            f.write(f"🏆 {trusted_status}\n")
            f.write('-' * 80 + '\n')

# 10. Write single records summary
def write_single_records_summary(df, unmatched_records, out_path):
    if not unmatched_records:
        # print("No single records found.")
        with open(out_path, 'a', encoding='utf-8') as f:
            f.write(f'\n--- SINGLE RECORDS ---\n')
            f.write("No single records found.\n")
            f.write('-' * 80 + '\n')
        return
    with open(out_path, 'a', encoding='utf-8') as f:
        f.write(f'\n--- SINGLE RECORDS ---\n')
        for record_id in sorted(unmatched_records):
            record = df.loc[record_id].to_dict()
            f.write(f"🔶 Single Record ({record_id}):\n")
            f.write(f"{record}\n")
            f.write(f"Source Record: {record_id}\n")
            f.write(f"Trusted Record: {record_id}\n")
            f.write('-' * 80 + '\n')

# 11. Write golden records
def write_golden_records(df, clusters, out_path, survivorship_rules, priority_rule):
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('--- GOLDEN RECORDS ---\n')
        for idx, cluster in enumerate(clusters):
            record_ids = list(cluster)
            golden, trusted_id = create_golden_record(df, record_ids, survivorship_rules, priority_rule['conditions'])
            f.write(f"🔶 Golden Record for Cluster {idx + 1} (Records: {', '.join(map(str, record_ids))}):\n")
            f.write(f"{golden}\n")
            f.write(f"Source Records: {', '.join(map(str, record_ids))}\n")
            f.write(f"Trusted Record: {trusted_id if trusted_id else 'None (survivorship applied)' if len(record_ids) > 1 else str(record_ids[0])}\n")
            f.write('-' * 80 + '\n')

# Write outputs


def process_write_outputs(df, features, yaml_path, out_path):

    TIMEIS = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
    # out_path = 'D:\\mygit\\easymdm\\out\\'
    # CONFIG_PATH = 'D:\\mygit\\OpenMDM\\mdm\\matching_identity\\config_mdm29.yml'


    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    priority_rule = config['priority_rule']
    date_column = config['survivorship']['rules'][0]['column']
    survivorship_rules = {rule['column']: rule['strategy'] for rule in config['survivorship']['rules']}

    summary_path = f"{out_path}detail_summary_{TIMEIS}.txt"
    golden_path = f"{out_path}golden_records_{TIMEIS}.txt"

    # 7. Group records into clusters
    G = nx.Graph()
    auto_merge_pairs = [(row.name[0], row.name[1]) for _, row in features[features['match_category'] == 'auto_merge'].iterrows()]
    review_pairs = [(row.name[0], row.name[1]) for _, row in features[features['match_category'] == 'review'].iterrows()]
    # print("Auto-merge pairs:", auto_merge_pairs)
    # print("Review pairs:", review_pairs)

    # Only use auto_merge pairs for clustering
    G.add_edges_from(auto_merge_pairs)
    clusters = list(nx.connected_components(G))

    # Add single-record clusters for unmatched records, excluding those in review pairs
    review_records = set().union(*[(i, j) for i, j in review_pairs])
    all_records = set(df.index)
    matched_records = set().union(*clusters)
    unmatched_records = all_records - matched_records - review_records
    for record_id in unmatched_records:
        clusters.append({record_id})



    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write('')  # Clear file
    write_pairwise_summary(df, features, 'auto_merge', summary_path, priority_rule)
    write_pairwise_summary(df, features, 'review', summary_path, priority_rule)
    write_single_records_summary(df, unmatched_records, summary_path)
    write_golden_records(df, clusters, golden_path, survivorship_rules, priority_rule)
    print(f"📊 MDM Summary Report saved here: {summary_path}")
    print(f"📈 Golden Records saved here: {golden_path}")
