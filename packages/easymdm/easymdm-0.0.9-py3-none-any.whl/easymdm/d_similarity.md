# Record Linkage Processing Script

This script processes record linkage between pairs of records in a dataset using the `recordlinkage` library, with configurations specified in a YAML file. It computes similarity scores for specified columns and categorizes potential matches based on user-defined thresholds.

## Dependencies

The script relies on the following Python libraries:

- **pandas**: Used for data manipulation and handling DataFrame operations.
  - **Version**: Compatible with pandas >= 1.0.0.
  - **Purpose**: Manages input data and processes output results.
  - **Installation**: `pip install pandas`

- **pyyaml**: Parses YAML configuration files to load similarity and threshold settings.
  - **Version**: Compatible with PyYAML >= 5.0.
  - **Purpose**: Reads the YAML file to configure the record linkage process.
  - **Installation**: `pip install pyyaml`

- **recordlinkage**: Implements record linkage algorithms to compare records and compute similarity scores.
  - **Version**: Compatible with recordlinkage >= 0.15.
  - **Purpose**: Provides comparison methods (e.g., exact, string similarity) for record linkage.
  - **Installation**: `pip install recordlinkage`

*Note*: The `fuzzywuzzy` library is commented out in the code and not used in the current implementation.

## Function: `process_similarity`

### Description
The `process_similarity` function computes similarity scores between pairs of records in a DataFrame based on configurations defined in a YAML file. It uses the `recordlinkage` library to compare specified columns and categorizes the results into match categories based on score thresholds.

### Input Parameters
- **df** (`pandas.DataFrame`): The input DataFrame containing the records to compare. Each row represents a record, and columns contain fields to compare (e.g., `firstname`, `lastname`).
- **yaml_path** (`str`): Path to the YAML configuration file specifying the columns to compare, comparison methods, and thresholds for categorizing matches.
- **candidate_pairs** (`pandas.MultiIndex`): A MultiIndex object containing pairs of record indices to compare (e.g., `(0, 1)`, `(3, 4)`).

### Output
- **Returns**: A `pandas.DataFrame` containing:
  - Similarity scores for each comparison method (e.g., `firstname_sim`, `lastname_match`).
  - A `score` column with the mean similarity score across all compared columns.
  - A `match_category` column categorizing pairs as `non_match`, `review`, or `auto_merge` based on thresholds.

### Process Flow
1. **Load YAML Configuration**: Reads the YAML file to extract similarity configurations and thresholds.
2. **Configure Comparisons**: Sets up comparisons for each column using methods like `exact`, `jarowinkler`, or `levenshtein`.
3. **Compute Similarity**: Calculates similarity scores for the specified candidate pairs.
4. **Calculate Mean Score**: Computes the average similarity score across all comparison methods.
5. **Categorize Matches**: Assigns each pair to a category (`non_match`, `review`, `auto_merge`) based on the mean score and thresholds.

## YAML Configuration

The YAML file specifies the columns to compare, the comparison methods, and the thresholds for categorizing matches. Below is an example YAML configuration, followed by a comprehensive list of supported methods in the `recordlinkage` library.

### Example YAML
```yaml
similarity:
  - column: firstname
    method: jarowinkler
  - column: lastname
    method: jarowinkler
  - column: address
    method: jarowinkler
  - column: city
    method: levenshtein
  - column: zip
    method: exact
thresholds:
  review: 0.7
  auto_merge: 0.9
```

### Explanation of YAML Structure
- **similarity**: A list of dictionaries, each specifying:
  - `column`: The name of the column in the DataFrame to compare (e.g., `firstname`, `lastname`).
  - `method`: The comparison method to use (e.g., `exact`, `jarowinkler`, `levenshtein`).
- **thresholds**: A dictionary specifying score thresholds for categorizing matches:
  - `review`: Pairs with scores above this threshold are flagged for review.
  - `auto_merge`: Pairs with scores above this threshold are considered automatic matches.

### Supported Comparison Methods in `recordlinkage`
The `recordlinkage` library supports multiple comparison methods for string and exact matching. Below is a complete list of methods that can be used in the `method` field of the YAML configuration:

1. **exact**:
   - Compares two values for exact equality.
   - Output: 1 if identical, 0 otherwise.
   - Example YAML:
     ```yaml
     - column: zip
       method: exact
     ```

2. **jarowinkler**:
   - Computes the Jaro-Winkler similarity, which is suitable for short strings like names.
   - Output: A float between 0 and 1 (1 for identical strings).
   - Example YAML:
     ```yaml
     - column: firstname
       method: jarowinkler
     ```

3. **levenshtein**:
   - Computes the Levenshtein distance (edit distance) between two strings.
   - Output: A normalized similarity score between 0 and 1.
   - Example YAML:
     ```yaml
     - column: city
       method: levenshtein
     ```

4. **damerau_levenshtein**:
   - Similar to Levenshtein but also considers transpositions of adjacent characters.
   - Output: A normalized similarity score between 0 and 1.
   - Example YAML:
     ```yaml
     - column: address
       method: damerau_levenshtein
     ```

5. **qgram**:
   - Compares strings based on q-gram (substrings of length q) similarity.
   - Output: A normalized similarity score between 0 and 1.
   - Example YAML:
     ```yaml
     - column: lastname
       method: qgram
     ```

6. **cosine**:
   - Computes the cosine similarity between q-gram profiles of strings.
   - Output: A normalized similarity score between 0 and 1.
   - Example YAML:
     ```yaml
     - column: description
       method: cosine
     ```

7. **smith_waterman**:
   - Uses the Smith-Waterman algorithm for local sequence alignment.
   - Output: A normalized similarity score between 0 and 1.
   - Example YAML:
     ```yaml
     - column: notes
       method: smith_waterman
     ```

8. **lcs** (Longest Common Subsequence):
   - Measures similarity based on the longest common subsequence between two strings.
   - Output: A normalized similarity score between 0 and 1.
   - Example YAML:
     ```yaml
     - column: comments
       method: lcs
     ```

### Extended YAML Example
Below is an extended YAML configuration that incorporates all supported `recordlinkage` comparison methods:

```yaml
similarity:
  - column: firstname
    method: jarowinkler
  - column: lastname
    method: jarowinkler
  - column: address
    method: damerau_levenshtein
  - column: city
    method: levenshtein
  - column: zip
    method: exact
  - column: description
    method: cosine
  - column: notes
    method: smith_waterman
  - column: comments
    method: lcs
  - column: alias
    method: qgram
thresholds:
  review: 0.65
  auto_merge: 0.85
```

### Notes on YAML Configuration
- Ensure that the `column` names match the column names in the input DataFrame exactly.
- The `method` field must be one of the supported `recordlinkage` methods listed above.
- Thresholds (`review` and `auto_merge`) should be floats between 0 and 1, with `review` < `auto_merge`.
- The `score` is the mean of all similarity scores, so the number of columns compared affects the final score.

## Example Usage
```python
import pandas as pd
import recordlinkage
from recordlinkage.index import Block

# Sample DataFrame
data = {
    'firstname': ['John', 'Jon', 'Jane', 'John', 'Jhon'],
    'lastname': ['Smith', 'Smith', 'Doe', 'Smyth', 'Smith'],
    'address': ['123 Main St', '123 Main St', '456 Oak St', '123 Main St', '124 Main St'],
    'city': ['New York', 'New York', 'Boston', 'New York', 'New York'],
    'zip': ['10001', '10001', '02108', '10001', '10002']
}
df = pd.DataFrame(data)

# Generate candidate pairs (e.g., block on city)
indexer = Block('city')
candidate_pairs = indexer.index(df)

# Process similarity
yaml_path = 'config.yaml'
features = process_similarity(df, yaml_path, candidate_pairs)

# View results
print(features[['score', 'match_category']])
```

## Output Example
The output DataFrame (`features`) contains:
- Columns for each similarity comparison (e.g., `firstname_sim`, `zip_match`).
- A `score` column with the mean similarity score.
- A `match_category` column with values `non_match`, `review`, or `auto_merge`.

Example output for the above data (assuming the extended YAML configuration):
```
           score match_category
(0, 1)     0.95    auto_merge
(0, 3)     0.88    auto_merge
(0, 4)     0.72      review
(1, 3)     0.85    auto_merge
(1, 4)     0.67      review
(3, 4)     0.60    non_match
```

## Debugging and Notes
- The script includes commented-out debugging code to check for missing pairs or inspect detailed similarity scores.
- Ensure that `candidate_pairs` is a valid `pandas.MultiIndex` object generated by a `recordlinkage` indexer (e.g., `Block`, `SortedNeighbourhood`).
- The `recordlinkage` library is computationally intensive for large datasets. Use indexing techniques (e.g., blocking) to reduce the number of candidate pairs.