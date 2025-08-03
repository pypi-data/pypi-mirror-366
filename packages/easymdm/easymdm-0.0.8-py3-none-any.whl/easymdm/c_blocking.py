import yaml
import recordlinkage
from fuzzywuzzy import fuzz
import pandas as pd

def process_blocking(df, yaml_path):
    # Extract configurations

    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    blocking_columns = config['blocking']['columns']
    # Example processing based on config
    # print(blocking_columns)

    # Create a new column by concatenating the specified columns
    df['concat_column'] = df[blocking_columns].apply(lambda x: ' '.join(x.astype(str)).lower(), axis=1)


    # Initialize recordlinkage indexer
    indexer = recordlinkage.Index()

    # Custom blocking based on fuzzy matching
    # Since recordlinkage doesn't natively support fuzzy blocking, we implement a custom approach
    candidate_pairs = []

    # Compare all pairs (this can be optimized for large datasets)
    for i, row1 in df.iterrows():
        for j, row2 in df[df.index > i].iterrows():  # Avoid self-pairs and duplicates
            if fuzzy_match(row1, row2, 'concat_column', threshold=80):
                candidate_pairs.append((i, j))

    # Convert candidate pairs to MultiIndex
    candidate_pairs = pd.MultiIndex.from_tuples(candidate_pairs, names=['first', 'second'])
    # Print the number of candidate pairs
    print(f"🧮 Total candidate pairs after fuzzy blocking: {len(candidate_pairs)}")
    return candidate_pairs
    # print(df)


# Define a function to compute fuzzy similarity
def fuzzy_match(row1, row2, column='concat_column', threshold=80):
        """
        Compute fuzzy match score between two rows for the specified column.
        Returns True if score is above threshold, False otherwise.
        """
        score = fuzz.token_sort_ratio(row1[column], row2[column])
        return score >= threshold


if __name__ == '__main__':
    process_blocking()