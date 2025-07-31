# import pytest
# import pandas as pd
# from unittest.mock import patch, MagicMock
# from gcp_utils_sds.yoy import append_gcs_file_with_year, map_bq_to_pandas, cast_df_to_bq_types

# def test_map_bq_to_pandas_basic_types():
#     bq_types = {"a": "STRING", "b": "INTEGER", "c": "FLOAT", "d": "BOOLEAN"}
#     pandas_types = map_bq_to_pandas(bq_types)
#     assert pandas_types == {"a": "string", "b": "Int64", "c": "float64", "d": "boolean"}

# def test_cast_df_to_bq_types():
#     df = pd.DataFrame({"a": ["1", "2"], "b": [1.1, 2.2]})
#     dtype_map = {"a": "string", "b": "float64"}
#     result = cast_df_to_bq_types(df, dtype_map)
#     assert result["a"].dtype.name == "string"
#     assert result["b"].dtype.name == "float64"

# def test_append_gcs_file_with_year_success(monkeypatch):
#     # Prepare current and old data
#     current_df = pd.DataFrame({"id": [1], "val": [10]})
#     old_csv = "id,val\n2,20"
#     # Mock GCS
#     mock_blob = MagicMock()
#     mock_blob.download_as_bytes.return_value = old_csv.encode()
#     mock_bucket = MagicMock()
#     mock_bucket.blob.return_value = mock_blob
#     mock_client = MagicMock()
#     mock_client.bucket.return_value = mock_bucket
#     # Mock BigQuery schema
#     mock_bq_types = {"id": "INTEGER", "val": "INTEGER", "year": "STRING"}
#     monkeypatch.setattr("gcp_utils_sds.yoy.storage.Client", lambda: mock_client)
#     monkeypatch.setattr("gcp_utils_sds.yoy.get_bq_schema", lambda *a, **kw: mock_bq_types)
#     monkeypatch.setattr("gcp_utils_sds.yoy.map_bq_to_pandas", lambda bq: {"id": "Int64", "val": "Int64", "year": "string"})
#     monkeypatch.setattr("gcp_utils_sds.yoy.cast_df_to_bq_types", lambda df, dtypes: df.astype(dtypes))
#     # Run
#     result = append_gcs_file_with_year(
#         dataset_current="ds",
#         table_name_current="tbl",
#         bucket_name_old="bucket",
#         blob_path_old="star_assessment_results_24-25.csv",
#         current_df=current_df,
#         columns_to_drop_duplicates=["id"]
#     )
#     assert "year" in result.columns
#     assert set(result["id"]) == {1, 2}
#     # Allow for <NA> in the year column for current_df rows
#     year_set = set(result["year"])
#     assert "24-25" in year_set
#     assert len(year_set - {"24-25", pd.NA}) == 0  # Only '24-25' and <NA> allowed

# def test_append_gcs_file_with_year_bad_filename(monkeypatch):
#     current_df = pd.DataFrame({"id": [1], "val": [10]})
#     old_csv = "id,val\n2,20"
#     mock_blob = MagicMock()
#     mock_blob.download_as_bytes.return_value = old_csv.encode()
#     mock_bucket = MagicMock()
#     mock_bucket.blob.return_value = mock_blob
#     mock_client = MagicMock()
#     mock_client.bucket.return_value = mock_bucket
#     monkeypatch.setattr("gcp_utils_sds.yoy.storage.Client", lambda: mock_client)
#     monkeypatch.setattr("gcp_utils_sds.yoy.get_bq_schema", lambda *a, **kw: {"id": "INTEGER", "val": "INTEGER"})
#     monkeypatch.setattr("gcp_utils_sds.yoy.map_bq_to_pandas", lambda bq: {"id": "Int64", "val": "Int64"})
#     monkeypatch.setattr("gcp_utils_sds.yoy.cast_df_to_bq_types", lambda df, dtypes: df.astype(dtypes))
#     with pytest.raises(ValueError):
#         append_gcs_file_with_year(
#             dataset_current="ds",
#             table_name_current="tbl",
#             bucket_name_old="bucket",
#             blob_path_old="badfile.csv",
#             current_df=current_df
#         )

