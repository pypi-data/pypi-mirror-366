# sagikoza
![PyPI - Version](https://img.shields.io/pypi/v/sagikoza)

This is a Python library that automatically collects and obtains all public notices based on Japan's “Furikome Sagi Relief Act”
You can obtain account information contained in public notices for the past three months or one year, in a registered format or standardized format.

[日本語の説明はこちらを参照ください](https://note.com/newvillage/n/n6553ca45bd85)

## Features
- Fetching by year or for the latest 3 months
- Parsing of collected data
- Handling data by list of dictionary
- Retry support when fetching fails
- Ensure consistent ID assignment. This can support incremental updates.
- Standardization of account names fileds and date fields (optional)

## Supported Environments
- Python 3.8 or later

## Installation
Install from PyPI:
```shell
python -m pip install sagikoza
```

Latest from GitHub:
```shell
git clone https://github.com/new-village/sagikoza
cd sagikoza
python setup.py install
```

## Usage
### Fetch notices for a specific year.
Fetching notices for the year specified in the parameter. This parameter may be available after 2008.
```python
import sagikoza
accounts = sagikoza.fetch('2025')
print(accounts[:5])
# [{'uid': 'd06beb...', 'bank_name': 'みずほ銀行', 'name': 'グエン テイ ホアイ ニエン', 'name_alias': 'NGUYEN THI HOAI NHIEN' ...}, ...] 
```

### Fetch notices for the last 3 months
Fetching without arguments to get notices from the latest 3 months.
```python
import sagikoza
accounts = sagikoza.fetch()
print(accounts)
# [{'uid': 'd06beb...', 'bank_name': 'みずほ銀行', 'name': 'グエン テイ ホアイ ニエン', 'name_alias': 'NGUYEN THI HOAI NHIEN' ...}, ...] 
```

### Fetch raw data
If you want to fetch raw data before normalization, set the `normalize` parameter to `False` to skip the normalization process.
```python
import sagikoza
accounts = sagikoza.fetch('near3', normalize=False)
print(accounts)
# [{'uid': 'd06beb...', 'bank_name': 'みずほ銀行', 'name': 'ＮＧＵＹＥＮ　ＴＨＩ　ＨＯＡＩ　ＮＨＩＥＮ　（グエン　テイ　ホアイ　ニエン）', ...}, ...] 
```

### Save data example
I recommend you to use pandas's `to_parquet`, if you would like to save the data in local.
```python
import pandas as pd
import sagikoza
accounts = sagikoza.fetch()
df = pd.DataFrame(accounts)
df.to_parquet('accounts.parquet', index=False)
```

## Function Specification
- `fetch(year: str = "near3") -> list[dict]`
  - Specify a year (YYYY) or "near3" for the latest 3 months
  - Raises an exception on failure

## Internal Workflow
1. Fetch notice list (POST: sel_pubs.php)
2. Fetch submits by Financial Institutions (POST: pubs_dispatcher.php)
3. Fetch subjects (GET: pubs_basic_frame.php)
4. Fetch accounts of financial crime (POST: k_pubstype_01_detail.php, etc.)

Parameters required for each step are extracted from the HTML and used for subsequent page transitions.

## Logging
Uses Python's standard `logging` module. For detailed logs:
```python
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
import sagikoza
sagikoza.fetch()
```
By default, only WARNING and above are shown. For more detail, set `level=logging.DEBUG`.

## Notes
- This library retrieves data from public sources. Changes to the source website may affect functionality
- Accuracy and completeness of retrieved data are not guaranteed. Please use together with official information

## License
Apache License 2.0
- BeautifulSoup (MIT License)

## Contribution
Bug reports, feature requests, and pull requests are welcome. Please use GitHub Issues or Pull Requests.

## Reference
- [Furikome Sagi Relief Act Notices](https://furikomesagi.dic.go.jp/index.php)
