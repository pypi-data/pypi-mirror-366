# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from deepdiff import DeepDiff

from snowflake.snowflake_data_validation.redshift.extractor.metadata_extractor_redshift import (
    MetadataExtractorRedshift,
)
from snowflake.snowflake_data_validation.connector.connector_base import ConnectorBase
from snowflake.snowflake_data_validation.query.query_generator_base import QueryGeneratorBase
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputHandlerBase,
)
from snowflake.snowflake_data_validation.utils.constants import COLUMN_VALIDATED, Platform
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext


class TestMetadataExtractorRedshiftIntegration:

    def setup_method(self):
        self.mock_connector = Mock(spec=ConnectorBase)
        self.mock_query_generator = Mock(spec=QueryGeneratorBase)
        self.report_path = "/test/reports"
        
        with patch('snowflake.snowflake_data_validation.redshift.extractor.metadata_extractor_redshift.LOGGER'):
            self.extractor = MetadataExtractorRedshift(
                connector=self.mock_connector,
                query_generator=self.mock_query_generator,
                report_path=self.report_path,
            )  

    def test_init_integration(self):
        with patch('snowflake.snowflake_data_validation.redshift.extractor.metadata_extractor_redshift.LOGGER') as mock_logger:
            extractor = MetadataExtractorRedshift(
                connector=self.mock_connector,
                query_generator=self.mock_query_generator,
                report_path=self.report_path,
            )
            
            assert extractor is not None
            assert extractor.connector == self.mock_connector
            assert extractor.query_generator == self.mock_query_generator
            assert extractor.report_path == self.report_path
            assert extractor.platform == Platform.REDSHIFT
            assert hasattr(extractor, 'helper_dataframe')
            
            mock_logger.debug.assert_any_call("Initializing MetadataExtractorRedshift")
            mock_logger.debug.assert_any_call("MetadataExtractorRedshift initialized successfully")

    def test_init_with_empty_report_path(self):
        with patch('snowflake.snowflake_data_validation.redshift.extractor.metadata_extractor_redshift.LOGGER'):
            extractor = MetadataExtractorRedshift(
                connector=self.mock_connector,
                query_generator=self.mock_query_generator,
                report_path="",
            )
            
            assert extractor.report_path == ""
            assert extractor.platform == Platform.REDSHIFT

    def _create_mock_output_handler(self):
        mock_handler = Mock(spec=OutputHandlerBase)
        mock_handler.handle_message = Mock()
        return mock_handler

    def test_process_schema_query_result_integration(self):
        mock_output_handler = self._create_mock_output_handler()
        
        columns_names = ("TABLE_NAME", "COLUMN_NAME", "DATA_TYPE", "IS_NULLABLE", "COLUMN_DEFAULT")
        metadata_info = [
            ("users", "id", "integer", "NO", None),
            ("users", "username", "character varying", "NO", None),
            ("users", "email", "character varying", "YES", None),
            ("users", "created_at", "timestamp without time zone", "NO", "now()"),
            ("orders", "order_id", "bigint", "NO", None),
            ("orders", "user_id", "integer", "YES", None),
            ("orders", "amount", "numeric", "NO", "0.00"),
        ]
        
        result = [columns_names, metadata_info]
        
        df = self.extractor.process_schema_query_result(result, mock_output_handler)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 7
        expected_columns = ["TABLE_NAME", "COLUMN_NAME", "DATA_TYPE", "IS_NULLABLE", "COLUMN_DEFAULT"]
        assert list(df.columns) == expected_columns
        
        actual_dict = df.to_dict('records')
        expected_dict = [
            {"TABLE_NAME": "orders", "COLUMN_NAME": "amount", "DATA_TYPE": "numeric", "IS_NULLABLE": "NO", "COLUMN_DEFAULT": "0.00"},
            {"TABLE_NAME": "orders", "COLUMN_NAME": "order_id", "DATA_TYPE": "bigint", "IS_NULLABLE": "NO", "COLUMN_DEFAULT": None},
            {"TABLE_NAME": "orders", "COLUMN_NAME": "user_id", "DATA_TYPE": "integer", "IS_NULLABLE": "YES", "COLUMN_DEFAULT": None},
            {"TABLE_NAME": "users", "COLUMN_NAME": "created_at", "DATA_TYPE": "timestamp without time zone", "IS_NULLABLE": "NO", "COLUMN_DEFAULT": "now()"},
            {"TABLE_NAME": "users", "COLUMN_NAME": "email", "DATA_TYPE": "character varying", "IS_NULLABLE": "YES", "COLUMN_DEFAULT": None},
            {"TABLE_NAME": "users", "COLUMN_NAME": "id", "DATA_TYPE": "integer", "IS_NULLABLE": "NO", "COLUMN_DEFAULT": None},
            {"TABLE_NAME": "users", "COLUMN_NAME": "username", "DATA_TYPE": "character varying", "IS_NULLABLE": "NO", "COLUMN_DEFAULT": None}
        ]
        
        diff = DeepDiff(expected_dict, actual_dict, ignore_order=True)
        assert not diff, f"DataFrames differ: {diff}"

    def test_process_metrics_query_result_integration(self):
        mock_output_handler = self._create_mock_output_handler()
        expected_columns = [COLUMN_VALIDATED, "COUNT_METRIC", "SUM_METRIC", "AVG_METRIC", "MAX_METRIC", "MIN_METRIC"]
        result_columns = (COLUMN_VALIDATED, "COUNT_METRIC", "SUM_METRIC", "AVG_METRIC", "MAX_METRIC", "MIN_METRIC")
        result_data = [
            ("id", 1000, 500500, 500.5, 1000, 1),
            ("username", 1000, None, None, None, None),
            ("email", 950, None, None, None, None),
            ("amount", 500, 125000.50, 250.001, 999.99, 0.01),
            ("created_at", 1000, None, None, "2025-01-15 10:30:00", "2023-01-01 00:00:00"),
        ]
        
        result = [result_columns, result_data]
        
        df = self.extractor.process_metrics_query_result(result, mock_output_handler)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        assert list(df.columns) == expected_columns
        
        actual_dict = df.to_dict('records')
        expected_dict = [
            {COLUMN_VALIDATED: "AMOUNT", "COUNT_METRIC": 500, "SUM_METRIC": 125000.50, "AVG_METRIC": 250.001, "MAX_METRIC": 999.99, "MIN_METRIC": 0.01},
            {COLUMN_VALIDATED: "CREATED_AT", "COUNT_METRIC": 1000, "SUM_METRIC": np.nan, "AVG_METRIC": np.nan, "MAX_METRIC": "2025-01-15 10:30:00", "MIN_METRIC": "2023-01-01 00:00:00"},
            {COLUMN_VALIDATED: "EMAIL", "COUNT_METRIC": 950, "SUM_METRIC": np.nan, "AVG_METRIC": np.nan, "MAX_METRIC": None, "MIN_METRIC": None},
            {COLUMN_VALIDATED: "ID", "COUNT_METRIC": 1000, "SUM_METRIC": 500500, "AVG_METRIC": 500.5, "MAX_METRIC": 1000, "MIN_METRIC": 1},
            {COLUMN_VALIDATED: "USERNAME", "COUNT_METRIC": 1000, "SUM_METRIC": np.nan, "AVG_METRIC": np.nan, "MAX_METRIC": None, "MIN_METRIC": None}
        ]
        
        diff = DeepDiff(expected_dict, actual_dict, ignore_order=True, ignore_nan_inequality=True)
        assert not diff, f"DataFrames differ: {diff}"
        
    def test_process_table_column_metadata_result_integration(self):
        mock_output_handler = self._create_mock_output_handler()
        
        result_columns = ("COLUMN_NAME", "DATA_TYPE", "IS_NULLABLE", "CHARACTER_MAXIMUM_LENGTH", "NUMERIC_PRECISION", "NUMERIC_SCALE")
        result_data = [
            ("id", "integer", "NO", None, 32, 0),
            ("username", "character varying", "NO", 255, None, None),
            ("email", "character varying", "YES", 320, None, None),
            ("balance", "numeric", "NO", None, 10, 2),
            ("is_active", "boolean", "NO", None, None, None),
            ("created_at", "timestamp without time zone", "NO", None, None, None),
        ]
        
        result = [result_columns, result_data]
        
        df = self.extractor.process_table_column_metadata_result(result, mock_output_handler)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 6
        expected_columns = ["COLUMN_NAME", "DATA_TYPE", "IS_NULLABLE", "CHARACTER_MAXIMUM_LENGTH", "NUMERIC_PRECISION", "NUMERIC_SCALE"]
        assert list(df.columns) == expected_columns
        
        actual_dict = df.to_dict('records')
        expected_dict = [
            {"COLUMN_NAME": "id", "DATA_TYPE": "integer", "IS_NULLABLE": "NO", "CHARACTER_MAXIMUM_LENGTH": np.nan, "NUMERIC_PRECISION": 32.0, "NUMERIC_SCALE": 0.0},
            {"COLUMN_NAME": "username", "DATA_TYPE": "character varying", "IS_NULLABLE": "NO", "CHARACTER_MAXIMUM_LENGTH": 255.0, "NUMERIC_PRECISION": np.nan, "NUMERIC_SCALE": np.nan},
            {"COLUMN_NAME": "email", "DATA_TYPE": "character varying", "IS_NULLABLE": "YES", "CHARACTER_MAXIMUM_LENGTH": 320.0, "NUMERIC_PRECISION": np.nan, "NUMERIC_SCALE": np.nan},
            {"COLUMN_NAME": "balance", "DATA_TYPE": "numeric", "IS_NULLABLE": "NO", "CHARACTER_MAXIMUM_LENGTH": np.nan, "NUMERIC_PRECISION": 10.0, "NUMERIC_SCALE": 2.0},
            {"COLUMN_NAME": "is_active", "DATA_TYPE": "boolean", "IS_NULLABLE": "NO", "CHARACTER_MAXIMUM_LENGTH": np.nan, "NUMERIC_PRECISION": np.nan, "NUMERIC_SCALE": np.nan},
            {"COLUMN_NAME": "created_at", "DATA_TYPE": "timestamp without time zone", "IS_NULLABLE": "NO", "CHARACTER_MAXIMUM_LENGTH": np.nan, "NUMERIC_PRECISION": np.nan, "NUMERIC_SCALE": np.nan}
        ]
        
        diff = DeepDiff(expected_dict, actual_dict, ignore_nan_inequality=True)
        assert not diff, f"DataFrames differ: {diff}"