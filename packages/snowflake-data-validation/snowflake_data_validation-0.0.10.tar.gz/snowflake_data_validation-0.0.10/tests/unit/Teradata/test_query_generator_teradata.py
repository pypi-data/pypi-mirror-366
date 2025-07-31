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

"""Tests for QueryGeneratorTeradata."""

import pytest
from unittest.mock import Mock

from snowflake.snowflake_data_validation.teradata.query.query_generator_teradata import (
    QueryGeneratorTeradata,
)
from snowflake.snowflake_data_validation.utils.model.chunk import Chunk
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputHandlerBase,
)
from snowflake.snowflake_data_validation.connector.connector_base import ConnectorBase
from snowflake.snowflake_data_validation.utils.constants import Platform
from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.utils.context import Context


class TestQueryGeneratorTeradata:
    """Test cases for QueryGeneratorTeradata."""

    def setup_method(self):
        """Set up test fixtures."""
        self.query_generator = QueryGeneratorTeradata()

    def test_init(self):
        """Test QueryGeneratorTeradata initialization."""
        assert self.query_generator is not None
        assert self.query_generator.platform == Platform.TERADATA

    def test_cte_query_generator_error_handling(self):
        """Test that CTE query generation handles errors when sql_generator is None."""
        with pytest.raises(AttributeError):
            self.query_generator.cte_query_generator(
                metrics_templates=None,
                col_name="test_col",
                col_type="INTEGER",
                fully_qualified_name="test_db.test_table",
                where_clause="",
                has_where_clause=False,
                sql_generator=None,
            )

    def test_outer_query_generator_basic(self):
        """Test that outer query generation works with basic inputs."""
        cte_names = ["test_cte"]
        metrics = [["min", "max"]]
        result = self.query_generator.outer_query_generator(cte_names, metrics)
        assert "SELECT" in result
        assert "test_cte" in result
        assert "min" in result
        assert "max" in result

    def test_generate_metrics_query_error_handling(self):
        """Test that metrics query generation handles errors properly."""
        # Create mock table context with all required attributes
        mock_table_context = Mock(spec=TableContext)
        mock_table_context.columns_to_validate = []  # Empty list should cause exception
        mock_table_context.fully_qualified_name = "test_db.test_schema.test_table"
        mock_table_context.templates_loader_manager = Mock()
        mock_table_context.templates_loader_manager.metrics_templates = Mock()
        mock_table_context.where_clause = ""
        mock_table_context.has_where_clause = False
        mock_table_context.sql_generator = Mock()
        
        mock_connector = Mock(spec=ConnectorBase)
        
        with pytest.raises(Exception, match="Metrics templates are missing for the column data types"):
            self.query_generator.generate_metrics_query(
                table_context=mock_table_context,
                connector=mock_connector
            )

    def test_generate_compute_md5_query_not_implemented(self):
        """Test that MD5 computation query generation raises NotImplementedError."""
        mock_table_context = Mock(spec=TableContext)
        mock_table_context.get_chunk_collection.return_value = [
            Chunk(offset=0, fetch=1)
        ]

        with pytest.raises(NotImplementedError, match="MD5 computation not implemented for Teradata"):
            self.query_generator.generate_compute_md5_query(
                table_context=mock_table_context, other_table_name="other_table"
            )

    def test_generate_statement_table_chunks_md5_not_implemented(self):
        """Test that MD5 table creation query generation raises NotImplementedError."""
        mock_table_context = Mock(spec=TableContext)

        with pytest.raises(NotImplementedError, match="MD5 chunks table creation not implemented for Teradata"):
            self.query_generator.generate_statement_table_chunks_md5(
                table_context=mock_table_context
            )

    def test_generate_extract_chunks_md5_query_not_implemented(self):
        """Test that MD5 chunk extraction query generation raises NotImplementedError."""
        mock_table_context = Mock(spec=TableContext)

        with pytest.raises(NotImplementedError, match="MD5 chunks extraction not implemented for Teradata"):
            self.query_generator.generate_extract_chunks_md5_query(
                table_context=mock_table_context
            )

    def test_generate_extract_md5_rows_chunk_query_not_implemented(self):
        """Test that MD5 chunk row extraction query generation raises NotImplementedError."""
        mock_table_context = Mock(spec=TableContext)

        with pytest.raises(NotImplementedError, match="MD5 rows chunk extraction not implemented for Teradata"):
            self.query_generator.generate_extract_md5_rows_chunk_query(
                chunk_id="chunk1", table_context=mock_table_context
            )
