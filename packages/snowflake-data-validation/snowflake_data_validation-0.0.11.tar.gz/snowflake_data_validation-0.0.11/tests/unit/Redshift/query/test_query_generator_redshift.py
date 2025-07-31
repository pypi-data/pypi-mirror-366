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
from unittest.mock import Mock, patch

from snowflake.snowflake_data_validation.redshift.query.query_generator_redshift import (
    QueryGeneratorRedshift,
)
from snowflake.snowflake_data_validation.utils.constants import Platform
from snowflake.snowflake_data_validation.extractor.sql_queries_template_generator import (
    SQLQueriesTemplateGenerator,
)


class TestQueryGeneratorRedshift:

    def setup_method(self):
        self.query_generator = QueryGeneratorRedshift()

    def test_init(self):
        assert self.query_generator is not None
        assert self.query_generator.platform == Platform.REDSHIFT

    @patch('snowflake.snowflake_data_validation.redshift.query.query_generator_redshift.generate_cte_query')
    def test_cte_query_generator_success(self, mock_generate_cte):
        mock_metrics_templates = Mock()
        mock_sql_generator = Mock(spec=SQLQueriesTemplateGenerator)
        expected_result = ("SELECT * FROM test", "test_cte", ["metric1", "metric2"])
        mock_generate_cte.return_value = expected_result

        result = self.query_generator.cte_query_generator(
            metrics_templates=mock_metrics_templates,
            col_name="test_col",
            col_type="VARCHAR",
            fully_qualified_name="test_db.test_table",
            where_clause="",
            has_where_clause=False,
            sql_generator=mock_sql_generator,
        )

        assert result == expected_result
        mock_generate_cte.assert_called_once_with(
            metrics_templates=mock_metrics_templates,
            col_name="test_col",
            col_type="VARCHAR",
            fully_qualified_name="test_db.test_table",
            where_clause="",
            has_where_clause=False,
            sql_generator=mock_sql_generator,
        )

    @patch('snowflake.snowflake_data_validation.redshift.query.query_generator_redshift.generate_cte_query')
    def test_cte_query_generator_with_where_clause(self, mock_generate_cte):
        mock_metrics_templates = Mock()
        mock_sql_generator = Mock(spec=SQLQueriesTemplateGenerator)
        expected_result = ("SELECT * FROM test WHERE id > 0", "test_cte", ["metric1"])
        mock_generate_cte.return_value = expected_result

        result = self.query_generator.cte_query_generator(
            metrics_templates=mock_metrics_templates,
            col_name="test_col",
            col_type="INTEGER",
            fully_qualified_name="test_db.test_table",
            where_clause="WHERE id > 0",
            has_where_clause=True,
            sql_generator=mock_sql_generator,
        )

        assert result == expected_result
        mock_generate_cte.assert_called_once_with(
            metrics_templates=mock_metrics_templates,
            col_name="test_col",
            col_type="INTEGER",
            fully_qualified_name="test_db.test_table",
            where_clause="WHERE id > 0",
            has_where_clause=True,
            sql_generator=mock_sql_generator,
        )

    @patch('snowflake.snowflake_data_validation.redshift.query.query_generator_redshift.generate_cte_query')
    def test_cte_query_generator_no_query_generated(self, mock_generate_cte):
        mock_metrics_templates = Mock()
        mock_sql_generator = Mock(spec=SQLQueriesTemplateGenerator)
        mock_generate_cte.return_value = (None, None, None)

        result = self.query_generator.cte_query_generator(
            metrics_templates=mock_metrics_templates,
            col_name="test_col",
            col_type="UNKNOWN_TYPE",
            fully_qualified_name="test_db.test_table",
            where_clause="",
            has_where_clause=False,
            sql_generator=mock_sql_generator,
        )

        assert result == (None, None, None)

    @patch('snowflake.snowflake_data_validation.redshift.query.query_generator_redshift.generate_outer_query')
    def test_outer_query_generator_success(self, mock_generate_outer):
        expected_result = "SELECT * FROM cte1 UNION ALL SELECT * FROM cte2"
        mock_generate_outer.return_value = expected_result
        cte_names = ["cte1", "cte2"]
        metrics = [["metric1"], ["metric2"]]

        result = self.query_generator.outer_query_generator(cte_names, metrics)

        assert result == expected_result
        mock_generate_outer.assert_called_once_with(cte_names, metrics)

    @patch('snowflake.snowflake_data_validation.redshift.query.query_generator_redshift.generate_cte_query')
    def test_cte_query_generator_error_handling(self, mock_generate_cte):
        mock_metrics_templates = Mock()
        mock_sql_generator = Mock(spec=SQLQueriesTemplateGenerator)
        mock_generate_cte.side_effect = Exception("CTE generation failed")

        with pytest.raises(Exception, match="CTE generation failed"):
            self.query_generator.cte_query_generator(
                metrics_templates=mock_metrics_templates,
                col_name="test_col",
                col_type="VARCHAR",
                fully_qualified_name="test_db.test_table",
                where_clause="",
                has_where_clause=False,
                sql_generator=mock_sql_generator,
            )

    @patch('snowflake.snowflake_data_validation.redshift.query.query_generator_redshift.generate_outer_query')
    def test_outer_query_generator_error_handling(self, mock_generate_outer):
        mock_generate_outer.side_effect = Exception("Outer query generation failed")
        cte_names = ["cte1", "cte2"]
        metrics = [["metric1"], ["metric2"]]

        with pytest.raises(Exception, match="Outer query generation failed"):
            self.query_generator.outer_query_generator(cte_names, metrics)

    @patch('snowflake.snowflake_data_validation.redshift.query.query_generator_redshift.generate_cte_query')
    def test_cte_query_generator_with_none_parameters(self, mock_generate_cte):
        mock_generate_cte.return_value = (None, None, None)

        result = self.query_generator.cte_query_generator(
            metrics_templates=None,
            col_name=None,
            col_type=None,
            fully_qualified_name=None,
            where_clause=None,
            has_where_clause=False,
            sql_generator=None,
        )

        assert result == (None, None, None)