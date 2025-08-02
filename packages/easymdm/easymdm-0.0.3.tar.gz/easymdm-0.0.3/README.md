# easymdm







#### Prerequisite
Define a yaml file for configuration details like below, Need to pass its name and location to CLI as shown below

```
sqlite:
  - DB_PATH: 'D:\\path\\to\\database\\'
    DB_NAME: 'mydatabase.db'

blocking:
  columns:
    - first_name
    - last_name
similarity:
  - column: first_name
    method: jarowinkler
  - column: middle_name
    method: jarowinkler
  - column: last_name
    method: jarowinkler
  - column: address
    method: levenshtein
  - column: city
    method: jarowinkler
  - column: zip_code
    method: exact

thresholds:
  review: 0.6
  auto_merge: 0.8

survivorship:
  rules:
    - column: Last_Updated_On
      strategy: most_recent

priority_rule:
  conditions:
    - column: original
      value: 1
    - column: Address
      value: *STREET*

```
### CLI Run

```
For flat file
> uv run -m easymdm.cli --source file --name D:\\path\\to_your_file\\123.csv --config D:\\path\\to_your_config\\config.yaml

or for sqlite
uv run -m easymdm.cli --source sqlite --table main.slvr_personal_info --config D:\mygit\easymdm\config.yaml --outpath out/
```



### BUILD

```
easymdm> uv init --package

easymdm> uv build                          
Building source distribution...
Building wheel from source distribution...
Successfully built dist\easymdm-0.1.0.tar.gz
Successfully built dist\easymdm-0.1.0-py3-none-any.whl

```

Warnings

```
\fuzzywuzzy\fuzz.py:11: UserWarning: Using slow pure-python SequenceMatcher. Install python-Levenshtein to remove this warning
  warnings.warn('Using slow pure-python SequenceMatcher. Install python-Levenshtein to remove this warning')

```

CICD Action Messages

```
PleaseDeploytoPyPI


```