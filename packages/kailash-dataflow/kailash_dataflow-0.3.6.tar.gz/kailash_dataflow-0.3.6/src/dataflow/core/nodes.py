"""
DataFlow Node Generation

Dynamic node generation for database operations.
"""

from typing import Any, Dict, List, Optional, Type, Union

from kailash.nodes.base import Node, NodeParameter, NodeRegistry


class NodeGenerator:
    """Generates workflow nodes for DataFlow models."""

    def __init__(self, dataflow_instance):
        self.dataflow_instance = dataflow_instance

    def _normalize_type_annotation(self, type_annotation: Any) -> Type:
        """Normalize complex type annotations to simple types for NodeParameter.

        This function converts complex typing constructs like Optional[str], List[str],
        Dict[str, Any], etc. into simple Python types that NodeParameter can handle.

        Args:
            type_annotation: The type annotation from model field

        Returns:
            A simple Python type (str, int, bool, list, dict, etc.)
        """
        # Handle typing constructs
        if hasattr(type_annotation, "__origin__"):
            origin = type_annotation.__origin__
            args = getattr(type_annotation, "__args__", ())

            # Handle Optional[T] -> Union[T, None]
            if origin is Union:
                # Find the non-None type
                for arg in args:
                    if arg is not type(None):
                        return self._normalize_type_annotation(arg)
                # Fallback to str if all types are None
                return str

            # Handle List[T], Dict[K, V], etc. - return base container type
            elif origin in (list, List):
                return list
            elif origin in (dict, Dict):
                return dict
            elif origin in (tuple, tuple):
                return tuple
            elif origin in (set, frozenset):
                return set

            # Return the origin for other generic types
            return origin

        # Handle regular types
        elif isinstance(type_annotation, type):
            return type_annotation

        # Fallback to str for unknown types
        return str

    def generate_crud_nodes(self, model_name: str, fields: Dict[str, Any]):
        """Generate CRUD workflow nodes for a model."""
        nodes = {
            f"{model_name}CreateNode": self._create_node_class(
                model_name, "create", fields
            ),
            f"{model_name}ReadNode": self._create_node_class(
                model_name, "read", fields
            ),
            f"{model_name}UpdateNode": self._create_node_class(
                model_name, "update", fields
            ),
            f"{model_name}DeleteNode": self._create_node_class(
                model_name, "delete", fields
            ),
            f"{model_name}ListNode": self._create_node_class(
                model_name, "list", fields
            ),
        }

        # Register nodes with Kailash's NodeRegistry system
        for node_name, node_class in nodes.items():
            NodeRegistry.register(node_class, alias=node_name)
            # Also register in module namespace for direct imports
            globals()[node_name] = node_class
            # Store in DataFlow instance for testing
            self.dataflow_instance._nodes[node_name] = node_class

    def generate_bulk_nodes(self, model_name: str, fields: Dict[str, Any]):
        """Generate bulk operation nodes for a model."""
        nodes = {
            f"{model_name}BulkCreateNode": self._create_node_class(
                model_name, "bulk_create", fields
            ),
            f"{model_name}BulkUpdateNode": self._create_node_class(
                model_name, "bulk_update", fields
            ),
            f"{model_name}BulkDeleteNode": self._create_node_class(
                model_name, "bulk_delete", fields
            ),
            f"{model_name}BulkUpsertNode": self._create_node_class(
                model_name, "bulk_upsert", fields
            ),
        }

        # Register nodes with Kailash's NodeRegistry system
        for node_name, node_class in nodes.items():
            NodeRegistry.register(node_class, alias=node_name)
            globals()[node_name] = node_class
            # Store in DataFlow instance for testing
            self.dataflow_instance._nodes[node_name] = node_class

    def _create_node_class(
        self, model_name: str, operation: str, fields: Dict[str, Any]
    ) -> Type[Node]:
        """Create a workflow node class for a model operation."""

        # Store parent DataFlow instance in closure
        dataflow_instance = self.dataflow_instance

        class DataFlowNode(Node):
            """Auto-generated DataFlow node."""

            def __init__(self, **kwargs):
                # Set attributes before calling super().__init__() because
                # the parent constructor calls get_parameters() which needs these
                self.model_name = model_name
                self.operation = operation
                self.dataflow_instance = dataflow_instance
                self.model_fields = fields
                super().__init__(**kwargs)

            def validate_inputs(self, **kwargs) -> Dict[str, Any]:
                """Override validate_inputs to add SQL injection protection for DataFlow nodes.

                This method provides connection-level SQL injection protection by:
                1. Calling parent validation for type checking and required parameters
                2. Adding SQL injection detection and sanitization
                3. Preventing malicious SQL fragments in database parameters
                """
                import logging
                import re
                from typing import Any, Dict, List, Union

                logger = logging.getLogger(__name__)

                # First, call parent validation for standard checks
                validated_inputs = super().validate_inputs(**kwargs)

                # SQL injection patterns to detect
                sql_injection_patterns = [
                    r"(?i)(union\s+select)",  # UNION SELECT attacks
                    r"(?i)(select\s+\*?\s*from)",  # SELECT FROM attacks
                    r"(?i)(drop\s+table)",  # DROP TABLE attacks
                    r"(?i)(delete\s+from)",  # DELETE FROM attacks
                    r"(?i)(insert\s+into)",  # INSERT INTO attacks
                    r"(?i)(update\s+\w+\s+set)",  # UPDATE SET attacks
                    r"(?i)(exec\s*\()",  # EXEC() attacks
                    r"(?i)(script\s*>)",  # XSS in SQL context
                    r"(?i)(or\s+['\"]?1['\"]?\s*=\s*['\"]?1['\"]?)",  # OR 1=1 attacks
                    r"(?i)(and\s+['\"]?1['\"]?\s*=\s*['\"]?1['\"]?)",  # AND 1=1 attacks
                    r"(?i)(\;\s*(drop|delete|insert|update|exec))",  # Statement chaining
                    r"(?i)(--\s*$)",  # SQL comments for bypass
                    r"(?i)(/\*.*?\*/)",  # SQL block comments
                ]

                def sanitize_sql_input(value: Any, field_name: str) -> Any:
                    """Sanitize individual input value for SQL injection."""
                    if value is None:
                        return None
                    if not isinstance(value, str):
                        # For non-string types, only process if they could contain injection when converted
                        if isinstance(value, (int, float, bool)):
                            return value  # Safe types, return as-is
                        # For complex types, convert to string and sanitize, then return the sanitized string
                        value = str(value)

                    original_value = value

                    # Apply sanitization in specific order to avoid conflicts
                    # 1. Handle statement chaining first (most general)
                    value = re.sub(
                        r"(?i)(\;\s*(drop|delete|insert|update|exec))",
                        "; STATEMENT_BLOCKED",
                        value,
                    )

                    # 2. Handle specific SQL commands
                    value = re.sub(r"(?i)(union\s+select)", "UNION_SELECT", value)
                    value = re.sub(
                        r"(?i)(select\s+\*?\s*from)", "SELECT_FROM", value
                    )  # Add SELECT protection
                    value = re.sub(r"(?i)(drop\s+table)", "DROP_TABLE", value)
                    value = re.sub(r"(?i)(delete\s+from)", "DELETE_FROM", value)
                    value = re.sub(r"(?i)(insert\s+into)", "INSERT_INTO", value)
                    value = re.sub(r"(?i)(update\s+\w+\s+set)", "UPDATE_SET", value)
                    value = re.sub(r"(?i)(exec\s*\()", "EXEC_FUNC", value)

                    # 3. Handle logical operators
                    value = re.sub(
                        r"(?i)(or\s+['\"]?1['\"]?\s*=\s*['\"]?1['\"]?)",
                        "OR_1_EQUALS_1",
                        value,
                    )
                    value = re.sub(
                        r"(?i)(and\s+['\"]?1['\"]?\s*=\s*['\"]?1['\"]?)",
                        "AND_1_EQUALS_1",
                        value,
                    )

                    # 4. Handle comments
                    value = re.sub(r"(?i)(--\s*$)", "-- COMMENT_BLOCKED", value)
                    value = re.sub(r"(?i)(/\*.*?\*/)", "/* COMMENT_BLOCKED */", value)

                    # 5. Check if any patterns were found and log
                    if value != original_value:
                        for pattern in sql_injection_patterns:
                            if re.search(pattern, original_value):
                                logger.warning(
                                    f"Potential SQL injection detected in field '{field_name}': {pattern}"
                                )
                                break
                        logger.info(
                            f"Sanitized SQL injection in field '{field_name}': {original_value} -> {value}"
                        )

                    return value

                def sanitize_nested_structure(data: Any, field_path: str = "") -> Any:
                    """Recursively sanitize nested data structures."""
                    if isinstance(data, dict):
                        return {
                            key: sanitize_nested_structure(
                                value, f"{field_path}.{key}" if field_path else key
                            )
                            for key, value in data.items()
                        }
                    elif isinstance(data, list):
                        return [
                            sanitize_nested_structure(item, f"{field_path}[{i}]")
                            for i, item in enumerate(data)
                        ]
                    else:
                        return sanitize_sql_input(data, field_path)

                # Apply SQL injection protection to all validated inputs
                protected_inputs = {}
                for field_name, value in validated_inputs.items():
                    if field_name in ["filter", "data", "update"]:
                        # Special handling for complex database operation fields
                        protected_inputs[field_name] = sanitize_nested_structure(
                            value, field_name
                        )
                    else:
                        # Standard field sanitization
                        protected_inputs[field_name] = sanitize_sql_input(
                            value, field_name
                        )

                # Additional DataFlow-specific validations
                if operation == "create" or operation == "update":
                    # Ensure no SQL injection in individual field values
                    for field_name, field_info in self.model_fields.items():
                        if field_name in protected_inputs:
                            value = protected_inputs[field_name]
                            if isinstance(value, str) and len(value) > 1000:
                                logger.warning(
                                    f"Suspiciously long input in field '{field_name}': {len(value)} characters"
                                )

                elif operation == "list":
                    # Special validation for filter parameters
                    filter_dict = protected_inputs.get("filter", {})
                    if isinstance(filter_dict, dict):
                        # Validate MongoDB-style operators are safe
                        for field, filter_value in filter_dict.items():
                            if isinstance(filter_value, dict):
                                for op, op_value in filter_value.items():
                                    if op.startswith("$"):
                                        # Validate MongoDB-style operators
                                        allowed_ops = [
                                            "$eq",
                                            "$ne",
                                            "$gt",
                                            "$gte",
                                            "$lt",
                                            "$lte",
                                            "$in",
                                            "$nin",
                                            "$regex",
                                            "$exists",
                                            "$not",
                                        ]
                                        if op not in allowed_ops:
                                            raise ValueError(
                                                f"Unsafe filter operator '{op}' in field '{field}'"
                                            )

                elif operation.startswith("bulk_"):
                    # Validate bulk data doesn't contain injection
                    bulk_data = protected_inputs.get("data", [])
                    if isinstance(bulk_data, list):
                        for i, record in enumerate(bulk_data):
                            if isinstance(record, dict):
                                for field_name, value in record.items():
                                    if isinstance(value, str):
                                        # Check each field in bulk data
                                        sanitized = sanitize_sql_input(
                                            value, f"data[{i}].{field_name}"
                                        )
                                        if sanitized != value:
                                            bulk_data[i][field_name] = sanitized

                logger.debug(
                    f"DataFlow SQL injection protection applied to {operation} operation"
                )
                return protected_inputs

            def get_parameters(self) -> Dict[str, NodeParameter]:
                """Define parameters for this DataFlow node."""
                if operation == "create":
                    # Generate parameters from model fields
                    params = {}
                    for field_name, field_info in self.model_fields.items():
                        if field_name not in ["id", "created_at", "updated_at"]:
                            # Normalize complex type annotations to simple types
                            normalized_type = self.dataflow_instance._node_generator._normalize_type_annotation(
                                field_info["type"]
                            )
                            params[field_name] = NodeParameter(
                                name=field_name,
                                type=normalized_type,
                                required=field_info.get("required", True),
                                default=field_info.get("default"),
                                description=f"{field_name} for the record",
                            )
                    return params

                elif operation == "read":
                    return {
                        "id": NodeParameter(
                            name="id",
                            type=int,
                            required=False,
                            default=1,
                            description="ID of record to read",
                        )
                    }

                elif operation == "update":
                    params = {
                        "id": NodeParameter(
                            name="id",
                            type=int,
                            required=False,
                            default=1,
                            description="ID of record to update",
                        )
                    }
                    # Add all model fields as optional update parameters
                    for field_name, field_info in self.model_fields.items():
                        if field_name not in ["id", "created_at", "updated_at"]:
                            # Normalize complex type annotations to simple types
                            normalized_type = self.dataflow_instance._node_generator._normalize_type_annotation(
                                field_info["type"]
                            )
                            params[field_name] = NodeParameter(
                                name=field_name,
                                type=normalized_type,
                                required=False,
                                description=f"New {field_name} for the record",
                            )
                    return params

                elif operation == "delete":
                    return {
                        "id": NodeParameter(
                            name="id",
                            type=int,
                            required=False,
                            default=1,
                            description="ID of record to delete",
                        )
                    }

                elif operation == "list":
                    return {
                        "limit": NodeParameter(
                            name="limit",
                            type=int,
                            required=False,
                            default=10,
                            description="Maximum number of records to return",
                        ),
                        "offset": NodeParameter(
                            name="offset",
                            type=int,
                            required=False,
                            default=0,
                            description="Number of records to skip",
                        ),
                        "order_by": NodeParameter(
                            name="order_by",
                            type=list,
                            required=False,
                            default=[],
                            description="Fields to sort by",
                        ),
                        "filter": NodeParameter(
                            name="filter",
                            type=dict,
                            required=False,
                            default={},
                            description="Filter criteria",
                        ),
                        "enable_cache": NodeParameter(
                            name="enable_cache",
                            type=bool,
                            required=False,
                            default=True,
                            description="Whether to enable query caching",
                        ),
                        "cache_ttl": NodeParameter(
                            name="cache_ttl",
                            type=int,
                            required=False,
                            default=None,
                            description="Cache TTL in seconds",
                        ),
                        "cache_key": NodeParameter(
                            name="cache_key",
                            type=str,
                            required=False,
                            default=None,
                            description="Override cache key",
                        ),
                        "count_only": NodeParameter(
                            name="count_only",
                            type=bool,
                            required=False,
                            default=False,
                            description="Return count only",
                        ),
                    }

                elif operation.startswith("bulk_"):
                    return {
                        "data": NodeParameter(
                            name="data",
                            type=list,
                            required=False,
                            default=[],
                            description="List of records for bulk operation",
                        ),
                        "batch_size": NodeParameter(
                            name="batch_size",
                            type=int,
                            required=False,
                            default=1000,
                            description="Batch size for bulk operations",
                        ),
                        "conflict_resolution": NodeParameter(
                            name="conflict_resolution",
                            type=str,
                            required=False,
                            default="skip",
                            description="How to handle conflicts",
                        ),
                        "filter": NodeParameter(
                            name="filter",
                            type=dict,
                            required=False,
                            default={},
                            description="Filter for bulk update/delete",
                        ),
                        "update": NodeParameter(
                            name="update",
                            type=dict,
                            required=False,
                            default={},
                            description="Update values for bulk update",
                        ),
                        "return_ids": NodeParameter(
                            name="return_ids",
                            type=bool,
                            required=False,
                            default=False,
                            description="Whether to return created record IDs",
                        ),
                    }

                return {}

            def run(self, **kwargs) -> Dict[str, Any]:
                """Execute the database operation using DataFlow components."""
                import logging

                from kailash.nodes.data.async_sql import AsyncSQLDatabaseNode

                logger = logging.getLogger(__name__)
                logger.info(f"Run called with kwargs: {kwargs}")

                # Apply tenant filtering if multi-tenant mode
                if self.dataflow_instance.config.security.multi_tenant:
                    tenant_id = self.dataflow_instance._tenant_context.get("tenant_id")
                    if tenant_id and "filter" in kwargs:
                        kwargs["filter"]["tenant_id"] = tenant_id

                # Execute database operations using DataFlow components
                if operation == "create":
                    # Use DataFlow's insert SQL generation and AsyncSQLDatabaseNode for execution
                    try:
                        # Get connection string
                        connection_string = (
                            self.dataflow_instance.config.database.get_connection_url(
                                self.dataflow_instance.config.environment
                            )
                        )

                        # Detect database type for SQL generation
                        database_type = self.dataflow_instance._detect_database_type()

                        # Use DataFlow's insert SQL generation
                        query = self.dataflow_instance._generate_insert_sql(
                            model_name, database_type
                        )

                        # Get field names (exclude auto-generated fields)
                        field_names = [
                            k
                            for k in kwargs.keys()
                            if k not in ["id", "created_at", "updated_at"]
                        ]
                        values = [kwargs[k] for k in field_names]

                        # Execute using AsyncSQLDatabaseNode (synchronous wrapper)
                        sql_node = AsyncSQLDatabaseNode(
                            node_id=f"{model_name}_{operation}_sql",
                            connection_string=connection_string,
                            query=query,
                            params=values,
                            fetch_mode="one",  # RETURNING clause should return one record
                            validate_queries=False,
                        )
                        result = sql_node.execute()

                        if result and "result" in result and "data" in result["result"]:
                            row = result["result"]["data"]
                            if isinstance(row, list) and len(row) > 0:
                                row = row[0]

                            if row:
                                # Invalidate cache after successful create
                                cache_integration = getattr(
                                    self.dataflow_instance, "_cache_integration", None
                                )
                                if cache_integration:
                                    cache_integration.invalidate_model_cache(
                                        model_name, "create", row
                                    )

                                # Return the created record with all fields
                                return {**kwargs, **row}

                        # Fall back to basic response if no data returned
                        return {"id": None, **kwargs}

                    except Exception as e:
                        logger.error(f"Create operation failed: {e}")
                        return {"success": False, "error": str(e)}

                elif operation == "read":
                    record_id = kwargs.get("id", 1)

                    # Get connection string
                    connection_string = (
                        self.dataflow_instance.config.database.get_connection_url(
                            self.dataflow_instance.config.environment
                        )
                    )

                    # Detect database type for SQL generation
                    database_type = self.dataflow_instance._detect_database_type()

                    # Use DataFlow's select SQL generation
                    select_templates = self.dataflow_instance._generate_select_sql(
                        model_name, database_type
                    )
                    query = select_templates["select_by_id"]

                    sql_node = AsyncSQLDatabaseNode(
                        node_id=f"{model_name}_{operation}_sql",
                        connection_string=connection_string,
                        query=query,
                        params=[record_id],
                        fetch_mode="one",
                        validate_queries=False,
                    )
                    result = sql_node.execute()

                    if result and "result" in result and "data" in result["result"]:
                        row = result["result"]["data"]
                        if isinstance(row, list) and len(row) > 0:
                            row = row[0]
                        if row:
                            # Return the row data with 'found' key as expected by tests
                            return {**row, "found": True}
                    return {"id": record_id, "found": False}

                elif operation == "update":
                    record_id = kwargs.get("id", 1)
                    updates = {
                        k: v
                        for k, v in kwargs.items()
                        if k != "id" and k not in ["created_at", "updated_at"]
                    }

                    if updates:
                        # Get connection string
                        connection_string = (
                            self.dataflow_instance.config.database.get_connection_url(
                                self.dataflow_instance.config.environment
                            )
                        )

                        # Detect database type for SQL generation
                        database_type = self.dataflow_instance._detect_database_type()

                        # Get table name
                        table_name = self.dataflow_instance._class_name_to_table_name(
                            model_name
                        )

                        # Build dynamic UPDATE query for only the fields being updated
                        field_names = list(updates.keys())
                        if database_type.lower() == "postgresql":
                            set_clauses = [
                                f"{name} = ${i+1}" for i, name in enumerate(field_names)
                            ]
                            where_clause = f"WHERE id = ${len(field_names)+1}"
                            updated_at_clause = "updated_at = CURRENT_TIMESTAMP"
                            # Get all field names for RETURNING clause
                            all_fields = self.dataflow_instance.get_model_fields(
                                model_name
                            )
                            all_columns = list(all_fields.keys())
                            query = f"UPDATE {table_name} SET {', '.join(set_clauses + [updated_at_clause])} {where_clause} RETURNING {', '.join(all_columns)}"
                        elif database_type.lower() == "mysql":
                            set_clauses = [f"{name} = %s" for name in field_names]
                            where_clause = "WHERE id = %s"
                            updated_at_clause = "updated_at = NOW()"
                            query = f"UPDATE {table_name} SET {', '.join(set_clauses + [updated_at_clause])} {where_clause}"
                        else:  # sqlite
                            set_clauses = [f"{name} = ?" for name in field_names]
                            where_clause = "WHERE id = ?"
                            updated_at_clause = "updated_at = CURRENT_TIMESTAMP"
                            query = f"UPDATE {table_name} SET {', '.join(set_clauses + [updated_at_clause])} {where_clause}"

                        # Prepare parameters: field values first, then ID
                        values = list(updates.values()) + [record_id]

                        sql_node = AsyncSQLDatabaseNode(
                            node_id=f"{model_name}_{operation}_sql",
                            connection_string=connection_string,
                            query=query,
                            params=values,
                            fetch_mode="one",
                            validate_queries=False,
                        )
                        result = sql_node.execute()

                        if result and "result" in result and "data" in result["result"]:
                            row = result["result"]["data"]
                            if isinstance(row, list) and len(row) > 0:
                                row = row[0]
                            if row:
                                # Invalidate cache after successful update
                                cache_integration = getattr(
                                    self.dataflow_instance, "_cache_integration", None
                                )
                                if cache_integration:
                                    cache_integration.invalidate_model_cache(
                                        model_name, "update", row
                                    )

                                # Merge the update values with the returned row data
                                # and add 'updated' key as expected by tests
                                result_data = {**kwargs, **row, "updated": True}
                                return result_data

                    return {"id": record_id, "updated": False}

                elif operation == "delete":
                    record_id = kwargs.get("id", 1)

                    # Get connection string
                    connection_string = (
                        self.dataflow_instance.config.database.get_connection_url(
                            self.dataflow_instance.config.environment
                        )
                    )

                    # Detect database type for SQL generation
                    database_type = self.dataflow_instance._detect_database_type()

                    # Use DataFlow's delete SQL generation and add RETURNING clause for PostgreSQL
                    delete_templates = self.dataflow_instance._generate_delete_sql(
                        model_name, database_type
                    )
                    query = delete_templates["delete_by_id"]

                    # Add RETURNING clause for PostgreSQL to get confirmation
                    if database_type.lower() == "postgresql":
                        query += " RETURNING id"

                    sql_node = AsyncSQLDatabaseNode(
                        node_id=f"{model_name}_{operation}_sql",
                        connection_string=connection_string,
                        query=query,
                        params=[record_id],
                        fetch_mode="one",
                        validate_queries=False,
                    )
                    result = sql_node.execute()

                    if result and "result" in result and "data" in result["result"]:
                        row = result["result"]["data"]
                        if isinstance(row, list) and len(row) > 0:
                            row = row[0]
                        if row:
                            # Invalidate cache after successful delete
                            cache_integration = getattr(
                                self.dataflow_instance, "_cache_integration", None
                            )
                            if cache_integration:
                                cache_integration.invalidate_model_cache(
                                    model_name, "delete", {"id": record_id}
                                )

                            return {"id": record_id, "deleted": True}
                    return {"id": record_id, "deleted": False}

                elif operation == "list":
                    limit = kwargs.get("limit", 10)
                    offset = kwargs.get("offset", 0)
                    filter_dict = kwargs.get("filter", {})
                    order_by = kwargs.get("order_by", [])
                    enable_cache = kwargs.get("enable_cache", True)
                    cache_ttl = kwargs.get("cache_ttl")
                    cache_key_override = kwargs.get("cache_key")
                    count_only = kwargs.get("count_only", False)

                    # Fix parameter type issues
                    import json

                    if isinstance(order_by, str):
                        try:
                            order_by = json.loads(order_by) if order_by.strip() else []
                        except (json.JSONDecodeError, ValueError):
                            order_by = []

                    if isinstance(filter_dict, str):
                        try:
                            filter_dict = (
                                json.loads(filter_dict) if filter_dict.strip() else {}
                            )
                        except (json.JSONDecodeError, ValueError):
                            filter_dict = {}

                    # Debug logging
                    logger.info(f"List operation - filter_dict: {filter_dict}")
                    logger.info(f"List operation - order_by: {order_by}")

                    # Use QueryBuilder if filters are provided
                    if filter_dict:
                        from ..database.query_builder import create_query_builder

                        # Get table name from DataFlow instance
                        table_name = self.dataflow_instance._class_name_to_table_name(
                            model_name
                        )

                        # Create query builder
                        builder = create_query_builder(
                            table_name, self.dataflow_instance.config.database.url
                        )

                        # Apply filters using MongoDB-style operators
                        for field, value in filter_dict.items():
                            if isinstance(value, dict):
                                # Handle MongoDB-style operators
                                for op, op_value in value.items():
                                    builder.where(field, op, op_value)
                            else:
                                # Simple equality
                                builder.where(field, "$eq", value)

                        # Apply ordering
                        if order_by:
                            for order_spec in order_by:
                                if isinstance(order_spec, dict):
                                    for field, direction in order_spec.items():
                                        dir_str = "DESC" if direction == -1 else "ASC"
                                        builder.order_by(field, dir_str)
                                else:
                                    builder.order_by(order_spec)
                        else:
                            builder.order_by("id", "DESC")

                        # Apply pagination
                        builder.limit(limit).offset(offset)

                        # Build query
                        if count_only:
                            query, params = builder.build_count()
                        else:
                            query, params = builder.build_select()
                    else:
                        # Simple query without filters using DataFlow SQL generation
                        database_type = self.dataflow_instance._detect_database_type()
                        select_templates = self.dataflow_instance._generate_select_sql(
                            model_name, database_type
                        )

                        if count_only:
                            query = select_templates["count_all"]
                            params = []
                        else:
                            # Build pagination query using template
                            if database_type.lower() == "postgresql":
                                query = select_templates[
                                    "select_with_pagination"
                                ].format(limit="$1", offset="$2")
                            elif database_type.lower() == "mysql":
                                query = select_templates[
                                    "select_with_pagination"
                                ].format(limit="%s", offset="%s")
                            else:  # sqlite
                                query = select_templates[
                                    "select_with_pagination"
                                ].format(limit="?", offset="?")
                            params = [limit, offset]

                    # Define executor function for cache integration
                    def execute_query():
                        connection_string = (
                            self.dataflow_instance.config.database.get_connection_url(
                                self.dataflow_instance.config.environment
                            )
                        )

                        # Debug logging
                        logger.info(f"Executing query: {query}")
                        logger.info(f"With params: {params}")

                        sql_node = AsyncSQLDatabaseNode(
                            node_id=f"{model_name}_{operation}_sql",
                            connection_string=connection_string,
                            query=query,
                            params=params,
                            fetch_mode="all" if not count_only else "one",
                            validate_queries=False,
                        )
                        sql_result = sql_node.execute()

                        if (
                            sql_result
                            and "result" in sql_result
                            and "data" in sql_result["result"]
                        ):
                            if count_only:
                                # Return count result
                                count_data = sql_result["result"]["data"]
                                if isinstance(count_data, list) and len(count_data) > 0:
                                    count_value = count_data[0]
                                    if isinstance(count_value, dict):
                                        count = count_value.get("count", 0)
                                    else:
                                        count = count_value
                                else:
                                    count = 0
                                return {"count": count}
                            else:
                                # Return list result
                                records = sql_result["result"]["data"]
                                return {
                                    "records": records,
                                    "count": len(records),
                                    "limit": limit,
                                }

                        # Default return
                        if count_only:
                            return {"count": 0}
                        else:
                            return {"records": [], "count": 0, "limit": limit}

                    # Check if cache integration is available
                    cache_integration = getattr(
                        self.dataflow_instance, "_cache_integration", None
                    )
                    if cache_integration and enable_cache:
                        # Use cache integration
                        return cache_integration.execute_with_cache(
                            model_name=model_name,
                            query=query,
                            params=params,
                            executor_func=execute_query,
                            cache_enabled=enable_cache,
                            cache_ttl=cache_ttl,
                            cache_key_override=cache_key_override,
                        )
                    else:
                        # Execute directly without caching
                        return execute_query()

                elif operation.startswith("bulk_"):
                    data = kwargs.get("data", [])
                    batch_size = kwargs.get("batch_size", 1000)

                    if operation == "bulk_create" and data:
                        # Implement real bulk create using database operations
                        try:
                            # Get connection string
                            connection_string = self.dataflow_instance.config.database.get_connection_url(
                                self.dataflow_instance.config.environment
                            )

                            # Detect database type for SQL generation
                            database_type = (
                                self.dataflow_instance._detect_database_type()
                            )

                            processed_count = 0
                            for record in data:
                                try:
                                    # Get table name
                                    table_name = self.dataflow_instance._class_name_to_table_name(
                                        model_name
                                    )

                                    # Get field names (exclude auto-generated fields)
                                    field_names = [
                                        k
                                        for k in record.keys()
                                        if k not in ["id", "created_at", "updated_at"]
                                    ]
                                    values = [record.get(k) for k in field_names]

                                    # Build dynamic INSERT query for only the fields being provided
                                    columns = ", ".join(field_names)
                                    if database_type.lower() == "postgresql":
                                        placeholders = ", ".join(
                                            [f"${i+1}" for i in range(len(field_names))]
                                        )
                                        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING id, created_at, updated_at"
                                    elif database_type.lower() == "mysql":
                                        placeholders = ", ".join(
                                            ["%s"] * len(field_names)
                                        )
                                        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                                    else:  # sqlite
                                        placeholders = ", ".join(
                                            ["?"] * len(field_names)
                                        )
                                        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

                                    # Execute using AsyncSQLDatabaseNode
                                    sql_node = AsyncSQLDatabaseNode(
                                        node_id=f"{model_name}_{operation}_sql_{processed_count}",
                                        connection_string=connection_string,
                                        query=query,
                                        params=values,
                                        fetch_mode="one",  # RETURNING clause should return one record
                                        validate_queries=False,
                                    )
                                    result = sql_node.execute()

                                    if result and "result" in result:
                                        processed_count += 1
                                except Exception as e:
                                    logger.warning(
                                        f"Failed to insert bulk record {record}: {e}"
                                    )
                                    continue

                            # Invalidate cache after successful bulk create
                            cache_integration = getattr(
                                self.dataflow_instance, "_cache_integration", None
                            )
                            if cache_integration:
                                cache_integration.invalidate_model_cache(
                                    model_name,
                                    "bulk_create",
                                    {"processed": processed_count},
                                )

                            return {
                                "processed": processed_count,
                                "batch_size": batch_size,
                                "operation": operation,
                                "success": True,
                            }
                        except Exception as e:
                            logger.error(f"Bulk create operation failed: {e}")
                            return {
                                "processed": 0,
                                "batch_size": batch_size,
                                "operation": operation,
                                "success": False,
                                "error": str(e),
                            }
                    elif operation == "bulk_update" and (data or kwargs.get("filter")):
                        # Use DataFlow's bulk update operations
                        try:
                            bulk_result = self.dataflow_instance.bulk.bulk_update(
                                model_name=model_name,
                                data=data,
                                filter_criteria=kwargs.get("filter", {}),
                                update_values=kwargs.get("update", {}),
                                batch_size=batch_size,
                                **{
                                    k: v
                                    for k, v in kwargs.items()
                                    if k
                                    not in ["data", "batch_size", "filter", "update"]
                                },
                            )

                            return {
                                "processed": bulk_result.get("records_processed", 0),
                                "batch_size": batch_size,
                                "operation": operation,
                                "success": bulk_result.get("success", True),
                            }
                        except Exception as e:
                            logger.error(f"Bulk update operation failed: {e}")
                            return {
                                "processed": 0,
                                "batch_size": batch_size,
                                "operation": operation,
                                "success": False,
                                "error": str(e),
                            }
                    elif operation == "bulk_delete" and (data or kwargs.get("filter")):
                        # Use DataFlow's bulk delete operations
                        try:
                            bulk_result = self.dataflow_instance.bulk.bulk_delete(
                                model_name=model_name,
                                data=data,
                                filter_criteria=kwargs.get("filter", {}),
                                batch_size=batch_size,
                                **{
                                    k: v
                                    for k, v in kwargs.items()
                                    if k not in ["data", "batch_size", "filter"]
                                },
                            )

                            return {
                                "processed": bulk_result.get("records_processed", 0),
                                "batch_size": batch_size,
                                "operation": operation,
                                "success": bulk_result.get("success", True),
                            }
                        except Exception as e:
                            logger.error(f"Bulk delete operation failed: {e}")
                            return {
                                "processed": 0,
                                "batch_size": batch_size,
                                "operation": operation,
                                "success": False,
                                "error": str(e),
                            }
                    elif operation == "bulk_upsert" and data:
                        # Use DataFlow's bulk upsert operations
                        try:
                            bulk_result = self.dataflow_instance.bulk.bulk_upsert(
                                model_name=model_name,
                                data=data,
                                conflict_resolution=kwargs.get(
                                    "conflict_resolution", "skip"
                                ),
                                batch_size=batch_size,
                                **{
                                    k: v
                                    for k, v in kwargs.items()
                                    if k
                                    not in ["data", "batch_size", "conflict_resolution"]
                                },
                            )

                            return {
                                "processed": bulk_result.get("records_processed", 0),
                                "batch_size": batch_size,
                                "operation": operation,
                                "success": bulk_result.get("success", True),
                            }
                        except Exception as e:
                            logger.error(f"Bulk upsert operation failed: {e}")
                            return {
                                "processed": 0,
                                "batch_size": batch_size,
                                "operation": operation,
                                "success": False,
                                "error": str(e),
                            }
                    else:
                        # Fallback for unsupported bulk operations
                        result = {
                            "processed": len(data) if data else 0,
                            "batch_size": batch_size,
                            "operation": operation,
                            "success": False,
                            "error": f"Unsupported bulk operation: {operation}",
                        }
                        return result

                else:
                    result = {"operation": operation, "status": "executed"}
                    return result

        # Set dynamic class name and proper module
        DataFlowNode.__name__ = (
            f"{model_name}{operation.replace('_', ' ').title().replace(' ', '')}Node"
        )
        DataFlowNode.__qualname__ = DataFlowNode.__name__

        return DataFlowNode
