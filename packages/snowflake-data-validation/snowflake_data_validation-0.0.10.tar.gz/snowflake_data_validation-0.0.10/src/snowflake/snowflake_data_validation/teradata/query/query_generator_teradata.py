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

import logging

from typing import Union

from snowflake.snowflake_data_validation.query.query_generator_base import (
    QueryGeneratorBase,
)
from snowflake.snowflake_data_validation.teradata.extractor.teradata_cte_generator import (
    generate_cte_query,
    generate_outer_query,
)
from snowflake.snowflake_data_validation.utils.constants import Platform
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext


LOGGER = logging.getLogger(__name__)

class QueryGeneratorTeradata(QueryGeneratorBase):

    """Teradata-specific implementation of query generator."""

    def __init__(self):
        """Initialize the Teradata query generator."""
        super().__init__(platform=Platform.TERADATA)

    def cte_query_generator(
        self,
        metrics_templates,
        col_name: str,
        col_type: str,
        fully_qualified_name: str,
        where_clause: str,
        has_where_clause: bool,
        sql_generator,
    ) -> Union[tuple[str, str, list[str]], tuple[None, None, None]]:
        """Generate a CTE query for a specific column using Teradata CTE generator.

        Args:
            metrics_templates: DataFrame containing metrics templates.
            col_name (str): Column name.
            col_type (str): Column data type.
            fully_qualified_name (str): Fully qualified table name.
            where_clause (str): WHERE clause.
            has_where_clause (bool): Whether WHERE clause is present.
            sql_generator: SQL template generator instance.

        Returns:
            Tuple containing CTE query, CTE name, and metrics list, or (None, None, None) if no query generated.

        """
        return generate_cte_query(
            metrics_templates=metrics_templates,
            col_name=col_name,
            col_type=col_type,
            fully_qualified_name=fully_qualified_name,
            where_clause=where_clause,
            has_where_clause=has_where_clause,
            sql_generator=sql_generator,
        )

    def outer_query_generator(self, cte_names, metrics) -> str:
        """Generate an outer query combining CTEs using Teradata outer query generator.

        Args:
            cte_names: List of CTE names.
            metrics: List of metrics for each CTE.

        Returns:
            str: Generated outer query.

        """
        return generate_outer_query(cte_names, metrics)

    def generate_compute_md5_query(
        self, table_context: TableContext, other_table_name: str
    ) -> Union[str, list[str]]:
        """Not implemented for Teradata."""
        raise NotImplementedError("MD5 computation not implemented for Teradata")

    def generate_statement_table_chunks_md5(self, table_context: TableContext) -> str:
        """Not implemented for Teradata."""
        raise NotImplementedError("MD5 chunks table creation not implemented for Teradata")

    def generate_extract_chunks_md5_query(self, table_context: TableContext) -> str:
        """Not implemented for Teradata."""
        raise NotImplementedError("MD5 chunks extraction not implemented for Teradata")

    def generate_extract_md5_rows_chunk_query(
        self, chunk_id: str, table_context: TableContext
    ) -> str:
        """Not implemented for Teradata."""
        raise NotImplementedError("MD5 rows chunk extraction not implemented for Teradata")

    def _generate_compute_md5_chunk_query(
        self, table_context: TableContext, chunk_id: str, fetch: int, offset: int
    ) -> Union[str, list[str]]:
        """Not implemented for Teradata."""
        raise NotImplementedError()
