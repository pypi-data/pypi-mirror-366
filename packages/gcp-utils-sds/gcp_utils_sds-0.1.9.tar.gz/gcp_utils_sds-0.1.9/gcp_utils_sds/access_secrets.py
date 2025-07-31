from google.cloud import secretmanager
import logging
import google.auth
import json
from google.oauth2.service_account import Credentials

def access_secret_version(project_id, secret_id, version_id="latest"):
    """
    Fetches a secret from Google Cloud Secret Manager.
    """
    try:
        client = secretmanager.SecretManagerServiceClient()
        
        # Build the secret resource name
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        
        # Access the secret
        response = client.access_secret_version(name=name)
        
        # Decode the payload
        secret_value = response.payload.data.decode("UTF-8")

        secret_json = json.loads(secret_value)

        # Create credentials from the secret JSON
        credentials = Credentials.from_service_account_info(secret_json)
    
        return credentials
    except Exception as e:
        logging.error(f'Error accessing secret due to {e}')
        return None