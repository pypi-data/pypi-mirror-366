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

"""Tests for ConnectorTeradata."""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from snowflake.snowflake_data_validation.teradata.connector.connector_teradata import (
    ConnectorTeradata,
)
from snowflake.snowflake_data_validation.utils.constants import (
    FAILED_TO_EXECUTE_QUERY,
    CONNECTION_NOT_ESTABLISHED,
    FAILED_TO_EXECUTE_STATEMENT,
)


class TestConnectorTeradata:

    """Test cases for ConnectorTeradata."""

    def setup_method(self):
        """Set up test fixtures."""
        self.connector = ConnectorTeradata()

    def test_init(self):
        """Test ConnectorTeradata initialization."""
        assert self.connector.connection is None
        assert hasattr(self.connector, "tdml")

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_connect_success(self, mock_import_teradata):
        """Test successful connection to Teradata."""
        # Mock teradataml module
        mock_tdml = Mock()
        mock_import_teradata.return_value = mock_tdml

        # Mock successful connection
        mock_context = Mock()
        mock_tdml.create_context.return_value = mock_context

        # Mock successful verification query
        mock_dataframe = Mock()
        mock_tdml.DataFrame.from_query.return_value = mock_dataframe

        # Initialize connector with mocked tdml
        connector = ConnectorTeradata()
        connector.tdml = mock_tdml

        # Test connection
        connector.connect(
            host="test_host",
            user="test_user",
            password="test_password",
            database="test_db",
        )

        # Verify connection was created with correct parameters
        mock_tdml.create_context.assert_called_once_with(
            host="test_host",
            username="test_user",
            password="test_password",
            database="test_db",
            logmech="TD2",
        )

        # Verify connection verification query was executed
        mock_tdml.DataFrame.from_query.assert_called_once_with("SELECT 1 as test_col")

        assert connector.connection == mock_context

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_connect_missing_required_params(self, mock_import_teradata):
        """Test connection with missing required parameters."""
        mock_tdml = Mock()
        mock_import_teradata.return_value = mock_tdml

        connector = ConnectorTeradata()
        connector.tdml = mock_tdml

        with pytest.raises(ValueError) as exc_info:
            connector.connect(host="test_host", user="", password="test_password")

        assert "Host, user, and password are required connection parameters" in str(
            exc_info.value
        )

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_connect_default_database(self, mock_import_teradata):
        """Test connection with default database (DBC)."""
        mock_tdml = Mock()
        mock_import_teradata.return_value = mock_tdml

        mock_context = Mock()
        mock_tdml.create_context.return_value = mock_context
        mock_tdml.DataFrame.from_query.return_value = Mock()

        connector = ConnectorTeradata()
        connector.tdml = mock_tdml

        connector.connect(
            host="test_host",
            user="test_user",
            password="test_password"
            # No database specified - should default to "DBC"
        )

        mock_tdml.create_context.assert_called_once_with(
            host="test_host",
            username="test_user",
            password="test_password",
            database="DBC",  # Default database
            logmech="TD2",
        )

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_connect_connection_fails(self, mock_import_teradata):
        """Test connection when Teradata connection fails."""
        mock_tdml = Mock()
        mock_import_teradata.return_value = mock_tdml
        mock_tdml.create_context.side_effect = Exception("Connection failed")

        connector = ConnectorTeradata()
        connector.tdml = mock_tdml

        with pytest.raises(ConnectionError) as exc_info:
            connector.connect(
                host="test_host",
                user="test_user",
                password="test_password",
                database="test_db",
                max_attempts=1,
                delay_seconds=0.01,
                delay_multiplier=1.0,
            )

        assert "Failed to connect to Teradata: Connection failed" in str(exc_info.value)
        assert connector.connection is None

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_connect_verification_fails(self, mock_import_teradata):
        """Test connection when verification query fails."""
        mock_tdml = Mock()
        mock_import_teradata.return_value = mock_tdml

        mock_context = Mock()
        mock_tdml.create_context.return_value = mock_context
        mock_tdml.DataFrame.from_query.side_effect = Exception("Verification failed")

        connector = ConnectorTeradata()
        connector.tdml = mock_tdml

        with pytest.raises(ConnectionError) as exc_info:
            connector.connect(
                host="test_host",
                user="test_user",
                password="test_password",
                database="test_db",
                max_attempts=1,
                delay_seconds=0.01,
                delay_multiplier=1.0,
            )

        assert "Failed to verify Teradata connection" in str(exc_info.value)
        assert connector.connection is None

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_execute_query_success(self, mock_import_teradata):
        """Test successful query execution."""
        mock_tdml = Mock()
        mock_import_teradata.return_value = mock_tdml

        # Mock successful query execution
        mock_result_df = Mock()
        mock_tdml.DataFrame.from_query.return_value = mock_result_df

        # Mock pandas DataFrame conversion
        mock_pandas_df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        mock_result_df.to_pandas.return_value = mock_pandas_df

        connector = ConnectorTeradata()
        connector.tdml = mock_tdml
        connector.connection = Mock()  # Simulate established connection

        column_names, results = connector.execute_query("SELECT * FROM test_table")

        # Verify query was executed
        mock_tdml.DataFrame.from_query.assert_called_once_with(
            "SELECT * FROM test_table"
        )
        mock_result_df.to_pandas.assert_called_once()

        # Verify results format
        expected_columns = ["col1", "col2"]
        expected_results = [(1, "a"), (2, "b"), (3, "c")]

        assert column_names == expected_columns
        assert results == expected_results

    def test_execute_query_no_connection(self):
        """Test query execution without established connection."""
        with pytest.raises(Exception) as exc_info:
            self.connector.execute_query("SELECT 1")

        assert (
            "Database connection is not established. Please call connect() first."
            in str(exc_info.value)
        )

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_execute_query_fails(self, mock_import_teradata):
        """Test query execution when query fails."""
        mock_tdml = Mock()
        mock_import_teradata.return_value = mock_tdml
        mock_tdml.DataFrame.from_query.side_effect = Exception("Query execution failed")

        connector = ConnectorTeradata()
        connector.tdml = mock_tdml
        connector.connection = Mock()  # Simulate established connection

        with pytest.raises(Exception) as exc_info:
            connector.execute_query("SELECT * FROM test_table")

        assert FAILED_TO_EXECUTE_QUERY in str(exc_info.value)

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_close_with_connection(self, mock_import_teradata):
        """Test closing connection when connection exists."""
        mock_tdml = Mock()
        mock_import_teradata.return_value = mock_tdml

        connector = ConnectorTeradata()
        connector.tdml = mock_tdml
        connector.connection = Mock()  # Simulate established connection

        connector.close()

        mock_tdml.remove_context.assert_called_once()

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_close_with_exception(self, mock_import_teradata):
        """Test closing connection when exception occurs during close."""
        mock_tdml = Mock()
        mock_import_teradata.return_value = mock_tdml
        mock_tdml.remove_context.side_effect = Exception("Close failed")

        connector = ConnectorTeradata()
        connector.tdml = mock_tdml
        connector.connection = Mock()  # Simulate established connection

        # Should not raise exception, only log warning
        connector.close()

        mock_tdml.remove_context.assert_called_once()

    def test_close_without_connection(self):
        """Test closing connection when no connection exists."""
        # Should not raise exception, only log debug message
        self.connector.close()

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_import_teradata_dependency(self, mock_import_teradata):
        """Test import of teradataml dependency."""
        mock_tdml = Mock()
        mock_import_teradata.return_value = mock_tdml

        connector = ConnectorTeradata()

        # Verify import_teradata was called during initialization
        mock_import_teradata.assert_called_once()
        assert connector.tdml == mock_tdml

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_execute_query_without_return_success(self, mock_import_teradata):
        mock_tdml = Mock()
        mock_import_teradata.return_value = mock_tdml

        # Mock successful query execution
        mock_result_df = Mock()
        mock_tdml.DataFrame.from_query.return_value = mock_result_df

        # Mock pandas DataFrame conversion
        mock_pandas_df = pd.DataFrame()
        mock_result_df.to_pandas.return_value = mock_pandas_df

        connector = ConnectorTeradata()
        connector.tdml = mock_tdml
        connector.connection = Mock()  # Simulate established connection

        connector.execute_query_no_return("CREATE TABLE TEST_TABLE (INDEX_ INTEGER)")

        # Verify query was executed
        mock_tdml.DataFrame.from_query.assert_called_once_with(
            "CREATE TABLE TEST_TABLE (INDEX_ INTEGER)"
        )

    def test_execute_query_without_return_no_connection_exception(self):
        with pytest.raises(Exception) as exc_info:
            self.connector.execute_query_no_return(
                "CREATE TABLE TEST_TABLE (INDEX_ INTEGER)"
            )

        assert str(exc_info.value) == CONNECTION_NOT_ESTABLISHED

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_execute_query_without_return_fails(self, mock_import_teradata):
        mock_tdml = Mock()
        mock_import_teradata.return_value = mock_tdml
        mock_tdml.DataFrame.from_query.side_effect = Exception("Query execution failed")

        connector = ConnectorTeradata()
        connector.tdml = mock_tdml
        connector.connection = Mock()  # Simulate established connection

        with pytest.raises(Exception) as exc_info:
            connector.execute_query_no_return(
                "CREATE TABLE TEST_TABLE (INDEX_ INTEGER)"
            )

        assert str(exc_info.value) == FAILED_TO_EXECUTE_QUERY

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_execute_statement_success(self, mock_import_teradata):
        mock_tdml = Mock()
        mock_import_teradata.return_value = mock_tdml

        # Mock successful query execution
        mock_result_df = Mock()
        mock_tdml.DataFrame.from_query.return_value = mock_result_df

        # Mock pandas DataFrame conversion
        mock_pandas_df = pd.DataFrame()
        mock_result_df.to_pandas.return_value = mock_pandas_df

        connector = ConnectorTeradata()
        connector.tdml = mock_tdml
        connector.connection = Mock()  # Simulate established connection

        connector.execute_statement("CREATE TABLE TEST_TABLE (INDEX_ INTEGER)")

        # Verify query was executed
        mock_tdml.DataFrame.from_query.assert_called_once_with(
            "CREATE TABLE TEST_TABLE (INDEX_ INTEGER)"
        )

    def test_execute_statement_no_connection_exception(self):
        with pytest.raises(Exception) as exc_info:
            self.connector.execute_statement("CREATE TABLE TEST_TABLE (INDEX_ INTEGER)")

        assert str(exc_info.value) == CONNECTION_NOT_ESTABLISHED

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_execute_statement_fails(self, mock_import_teradata):
        mock_tdml = Mock()
        mock_import_teradata.return_value = mock_tdml
        mock_tdml.DataFrame.from_query.side_effect = Exception("Query execution failed")

        connector = ConnectorTeradata()
        connector.tdml = mock_tdml
        connector.connection = Mock()  # Simulate established connection

        with pytest.raises(Exception) as exc_info:
            connector.execute_statement("CREATE TABLE TEST_TABLE (INDEX_ INTEGER)")

        assert str(exc_info.value) == FAILED_TO_EXECUTE_STATEMENT.format(
            statement="CREATE TABLE TEST_TABLE (INDEX_ INTEGER)"
        )
