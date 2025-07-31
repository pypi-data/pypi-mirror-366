# gcp_utils

Utilities for working with Google Cloud Platform (GCP).
Written in an effort to keep re-useable functions to a singular package. 

## Installation

```bash
pip install gcp_utils
```

## Features
- Upload and read CSVs from Google Cloud Storage
- Access secrets from Google Secret Manager
- Combine current and previous year GCS data

## Example Usage

```python
from gcp_utils import send_to_gcs, read_gcs_csv_to_df, access_secret_version, load_and_append_previous_year

# Upload a DataFrame to GCS
send_to_gcs('my-bucket', 'data/', my_dataframe, 'file.csv')

# Read a CSV from GCS
df = read_gcs_csv_to_df('gs://my-bucket/data/file.csv')

# Access a secret
creds = access_secret_version('my-project', 'my-secret')

# Combine current and previous year data
df = load_and_append_previous_year('my-bucket', 'etl/incoming/2024_file.csv')
```

## License
MIT
