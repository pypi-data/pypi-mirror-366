from unittest.mock import patch, MagicMock
from gcp_utils_sds.access_secrets import access_secret_version

def test_access_secret_version_returns_credentials():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.payload.data.decode.return_value = '{"type": "service_account", "project_id": "test"}'
    
    with patch('gcp_utils_sds.access_secrets.secretmanager.SecretManagerServiceClient', return_value=mock_client):
        mock_client.access_secret_version.return_value = mock_response
        with patch('gcp_utils_sds.access_secrets.Credentials.from_service_account_info') as mock_creds:
            mock_creds.return_value = 'mocked-creds'
            creds = access_secret_version('pid', 'sid', '1')
            mock_client.access_secret_version.assert_called_once()
            mock_creds.assert_called_once()
            assert creds == 'mocked-creds'

def test_access_secret_version_logs_error(caplog):
    with patch('gcp_utils_sds.access_secrets.secretmanager.SecretManagerServiceClient', side_effect=Exception('fail')):
        creds = access_secret_version('pid', 'sid', '1')
        assert creds is None or creds == False or creds == ''
        assert 'Error accessing secret due to fail' in caplog.text
