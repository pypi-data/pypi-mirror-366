
import pandas as pd
import logging
import os
from google.cloud import storage  # Ensure you have the Google Cloud Storage client library installed
from io import BytesIO
from io import TextIOWrapper


def send_to_gcs(bucket_name, save_path, frame, frame_name):
    """
    Uploads a DataFrame as a CSV file to a GCS bucket directly from memory.

    Args:
        bucket_name (str): The name of the GCS bucket.
        save_path (str): The path within the bucket where the file will be saved.
        frame (pd.DataFrame): The DataFrame to upload.
        frame_name (str): The name of the file to save.
    """
    if not frame.empty:
        client = storage.Client()

        try:
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(os.path.join(save_path, frame_name))
            blob.chunk_size = 5 * 1024 * 1024  # 5MB chunk size for large uploads

            buffer = BytesIO()
            text_buffer = TextIOWrapper(buffer, encoding='utf-8')
            frame.to_csv(text_buffer, index=False)
            text_buffer.flush()
            buffer.seek(0)

            blob.upload_from_file(buffer, content_type='text/csv')
            logging.info(f"{frame_name} uploaded to GCS bucket {bucket_name} at {save_path}/{frame_name}")
        except Exception as e:
            logging.error(f"Failed to upload {frame_name} to GCS bucket {bucket_name}: {e}")
        finally:
            buffer.close()
    else:
        logging.info(f"No data present in {frame_name} file")




def read_gcs_csv_to_df(gcs_uri, client=None):
  
    if client is None:
        client = storage.Client()

    # Parse bucket and path
    assert gcs_uri.startswith('gs://'), "GCS URI must start with 'gs://'"
    path_parts = gcs_uri[5:].split('/', 1)
    bucket_name = path_parts[0]
    blob_path = path_parts[1]

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    data = blob.download_as_bytes()
    df = pd.read_csv(BytesIO(data))
    return df



