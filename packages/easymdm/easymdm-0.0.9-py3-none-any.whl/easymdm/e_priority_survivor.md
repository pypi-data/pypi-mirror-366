# Master Data Management (MDM) Code Documentation

This document provides a step-by-step explanation of the provided Python code, which implements a Master Data Management (MDM) process for deduplicating and consolidating records into "golden records" using survivorship rules and priority conditions. The code uses libraries like `networkx`, `pandas`, `yaml`, and `datetime` to process data, form clusters, and generate output files.

## Overview
The code performs the following high-level tasks:
1. **Load and Process Data**: Reads a configuration file and a dataset, applies priority-based survivorship rules, and creates clusters of matching records.
2. **Apply Rules**: Uses priority rules to select trusted records and survivorship rules to create golden records.
3. **Generate Outputs**: Writes detailed summaries of matched and unmatched records and creates golden record files.

Below is a detailed breakdown of each function and the main processing logic.

---

## Step-by-Step Breakdown

### 1. Library Imports and Setup
The code begins by importing necessary libraries and configuring pandas:
- **`networkx`**: Used for clustering records based on matching pairs.
- **`yaml`**: Loads configuration settings from a YAML file.
- **`pandas`**: Handles data manipulation and storage.
- **`datetime`**: Generates timestamps for output file names.
- **Pandas Option**: Sets `future.no_silent_downcasting` to `True` to avoid silent type downcasting in pandas.

### 2. `apply_priority_rule` Function
**Purpose**: Identifies a single trusted record from a set of records based on priority conditions.

**Steps**:
- **Input**: Takes a DataFrame (`df`), a list of record IDs (`record_ids`), and priority conditions (`priority_conditions`).
- **Column Type Conversion**:
  - Iterates through priority conditions (e.g., `{'column': 'is_active', 'value': 1}`).
  - Checks if the specified column exists in the DataFrame.
  - Attempts to convert column values to match the expected value type (e.g., integer for `1`).
  - Skips date-like values (e.g., `2023-01-01`) to avoid incorrect conversions.
  - Converts values like `'0'`, `'1'`, `'0.0'`, `'1.0'`, or the expected value to the correct type.
- **Priority Rule Application**:
  - For each condition, checks if exactly one record has the expected value in the specified column.
  - Returns the ID of the matching record if found; otherwise, returns `None`.

**Example**:
If `priority_conditions = [{'column': 'is_active', 'value': 1}]`, and only one record has `is_active = 1`, that record’s ID is returned.

---

### 3. `create_golden_record` Function
**Purpose**: Creates a consolidated "golden record" from a cluster of records.

**Steps**:
- **Input**: Takes a DataFrame (`df`), a list of record IDs (`record_ids`), survivorship rules, and priority conditions.
- **Trusted Record Selection**:
  - If multiple records exist, calls `apply_priority_rule` to select a trusted record.
  - If only one record exists, uses it as the trusted record.
- **Golden Record Creation**:
  - If a trusted record is found, returns its data as the golden record.
  - Otherwise, builds a golden record by applying survivorship rules:
    - For columns with a `most_recent` strategy, selects the value with the latest date (parsed using `pd.to_datetime`).
    - For other columns, takes the first non-null value.
    - If all values are null, assigns `None`.

**Output**: Returns a dictionary representing the golden record and the trusted record ID.

**Example**:
For records `[1, 2]` with `survivorship_rules = {'last_updated': 'most_recent'}`, the function selects the most recent `last_updated` value and the first non-null value for other columns.

---

### 4. `write_pairwise_summary` Function
**Purpose**: Writes a summary of record pairs for a given match category (e.g., `auto_merge` or `review`).

**Steps**:
- **Input**: Takes a DataFrame (`df`), a features DataFrame (`features`), a match category, an output file path, and priority rule conditions.
- **Filtering and Sorting**:
  - Filters the `features` DataFrame for the specified `match_category`.
  - Sorts pairs (`first`, `second`) to ensure consistent ordering (e.g., `id_min`, `id_max`) and removes duplicates.
- **Writing Output**:
  - Appends to the output file.
  - For each pair, writes:
    - Record details for both records.
    - Similarity score and match category.
    - Trusted record ID (from `apply_priority_rule`) or "None" if no priority match.
  - If no pairs exist, writes a message indicating no pairs were found.

**Output File Format**:
```
--- AUTO_MERGE RECORDS ---
🔹 Record 1 (ID1): {...}
🔸 Record 2 (ID2): {...}
💡 Similarity Score: 0.95 | Match Category: auto_merge
🏆 Trusted Record: ID1
----------------------------------------
```

---

### 5. `write_single_records_summary` Function
**Purpose**: Writes a summary of unmatched (single) records.

**Steps**:
- **Input**: Takes a DataFrame (`df`), a set of unmatched record IDs, and an output file path.
- **Writing Output**:
  - Appends to the output file.
  - For each unmatched record, writes:
    - Record details.
    - Source and trusted record ID (same as the record ID, as it’s unmatched).
  - If no unmatched records exist, writes a message indicating none were found.

**Output File Format**:
```
--- SINGLE RECORDS ---
🔶 Single Record (ID1):
{...}
Source Record: ID1
Trusted Record: ID1
----------------------------------------
```

---

### 6. `write_golden_records` Function
**Purpose**: Writes golden records for each cluster of records.

**Steps**:
- **Input**: Takes a DataFrame (`df`), a list of clusters, an output file path, survivorship rules, and priority rule conditions.
- **Writing Output**:
  - Overwrites the output file.
  - For each cluster:
    - Calls `create_golden_record` to generate the golden record and trusted record ID.
    - Writes the golden record, source record IDs, and trusted record ID.
  - Handles single-record clusters and multi-record clusters differently for trusted record reporting.

**Output File Format**:
```
--- GOLDEN RECORDS ---
🔶 Golden Record for Cluster 1 (Records: ID1, ID2):
{...}
Source Records: ID1, ID2
Trusted Record: ID1
----------------------------------------
```

---

### 7. `process_write_outputs` Function
**Purpose**: Orchestrates the MDM process by loading configurations, clustering records, and generating output files.

**Steps**:
- **Load Configuration**:
  - Reads a YAML file containing priority rules and survivorship rules.
  - Extracts the date column and survivorship rules.
- **Output File Paths**:
  - Generates timestamped file paths for the summary (`detail_summary_YYYY-MM-DD_HH_MM_SS.txt`) and golden records (`golden_records_YYYY-MM-DD_HH_MM_SS.txt`).
- **Clustering**:
  - Creates a `networkx` graph (`G`) and adds edges for `auto_merge` pairs from the `features` DataFrame.
  - Identifies clusters using `nx.connected_components`.
  - Adds single-record clusters for unmatched records (excluding those in `review` pairs).
- **Writing Outputs**:
  - Clears the summary file.
  - Calls `write_pairwise_summary` for `auto_merge` and `review` categories.
  - Calls `write_single_records_summary` for unmatched records.
  - Calls `write_golden_records` for all clusters.
- **Print Output Paths**