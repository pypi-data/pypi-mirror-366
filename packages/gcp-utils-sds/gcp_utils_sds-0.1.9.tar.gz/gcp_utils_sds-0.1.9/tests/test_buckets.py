import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from gcp_utils_sds.buckets import send_to_gcs

def test_send_to_gcs_uploads_when_not_empty():
    df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    
    with patch('gcp_utils_sds.buckets.storage.Client', return_value=mock_client):
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        send_to_gcs('test-bucket', 'test/path', df, 'file.csv')
        mock_client.bucket.assert_called_once_with('test-bucket')
        mock_bucket.blob.assert_called_once()
        mock_blob.upload_from_file.assert_called_once()

def test_send_to_gcs_logs_when_empty(caplog):
    caplog.set_level("INFO")
    df = pd.DataFrame()
    with patch('gcp_utils_sds.buckets.storage.Client') as mock_client:
        send_to_gcs('test-bucket', 'test/path', df, 'file.csv')
        assert 'No data present in file.csv file' in caplog.text
