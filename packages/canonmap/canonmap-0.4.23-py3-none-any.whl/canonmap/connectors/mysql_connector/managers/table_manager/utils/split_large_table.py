# src/canonmap/connectors/mysql_connector/managers/table_manager/utils/split_large_table.py

import logging
from typing import List, Dict, Any, Tuple
import pandas as pd
from pathlib import Path

from canonmap.connectors.mysql_connector.mysql_connector import MySQLConnector
from canonmap.connectors.mysql_connector.managers.table_manager.validators.requests import CreateTableRequest
from canonmap.connectors.mysql_connector.managers.table_manager.utils.create_table_from_data import create_table_from_data_util
from canonmap.exceptions import TableManagerError

logger = logging.getLogger(__name__)

def split_large_table_util(
    original_request: CreateTableRequest,
    connector: MySQLConnector,
    max_columns_per_table: int = 50,
    strategy: str = "sequential"
) -> List[Dict[str, Any]]:
    """
    Split a large table with too many columns into smaller tables.
    
    Args:
        original_request: The original table creation request
        connector: MySQL connector instance
        max_columns_per_table: Maximum number of columns per split table
        strategy: Splitting strategy - "sequential" or "grouped"
        
    Returns:
        List of results from creating the split tables
    """
    database_name = original_request.database.name
    original_table_name = original_request.name
    data = original_request.data
    
    # Load the data
    if isinstance(data, str) and Path(data).exists():
        df = pd.read_csv(data, na_values=['', 'nan', 'NaN'], keep_default_na=True)
        df = df.where(pd.notnull(df), None)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    elif isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        raise TableManagerError(f"Unsupported data type: {type(data)}")
    
    total_columns = len(df.columns)
    logger.info(f"Splitting table '{original_table_name}' with {total_columns} columns into tables with max {max_columns_per_table} columns each")
    
    # Split columns based on strategy
    if strategy == "sequential":
        column_groups = split_columns_sequential(df.columns, max_columns_per_table)
    elif strategy == "grouped":
        column_groups = split_columns_grouped(df.columns, max_columns_per_table)
    else:
        raise TableManagerError(f"Unknown splitting strategy: {strategy}")
    
    results = []
    
    # Create tables for each group
    for i, column_group in enumerate(column_groups):
        # Create subset of data
        df_subset = df[column_group]
        
        # Create table name for this subset
        if len(column_groups) == 1:
            table_name = original_table_name
        else:
            table_name = f"{original_table_name}_part_{i+1:02d}"
        
        # Create new request for this subset
        subset_request = CreateTableRequest(
            database=original_request.database,
            name=table_name,
            data=df_subset,
            if_exists=original_request.if_exists,
            autoconnect=original_request.autoconnect
        )
        
        try:
            result = create_table_from_data_util(subset_request, connector, df_subset)
            result["table_name"] = table_name
            result["columns"] = list(column_group)
            result["column_count"] = len(column_group)
            results.append(result)
            logger.info(f"Created table '{table_name}' with {len(column_group)} columns")
        except Exception as e:
            logger.error(f"Failed to create table '{table_name}': {e}")
            results.append({
                "action": "error",
                "reason": "table_creation_failed",
                "table_name": table_name,
                "error": str(e)
            })
    
    return results

def split_columns_sequential(columns: List[str], max_columns: int) -> List[List[str]]:
    """
    Split columns sequentially into groups.
    
    Args:
        columns: List of column names
        max_columns: Maximum columns per group
        
    Returns:
        List of column groups
    """
    groups = []
    for i in range(0, len(columns), max_columns):
        group = columns[i:i + max_columns]
        groups.append(group)
    return groups

def split_columns_grouped(columns: List[str], max_columns: int) -> List[List[str]]:
    """
    Split columns into logical groups based on naming patterns.
    
    Args:
        columns: List of column names
        max_columns: Maximum columns per group
        
    Returns:
        List of column groups
    """
    # Identify common prefixes to group related columns
    prefix_groups = {}
    
    for col in columns:
        # Extract prefix (everything before the last underscore or the whole name)
        if '_' in col:
            prefix = '_'.join(col.split('_')[:-1])
        else:
            prefix = col
        
        if prefix not in prefix_groups:
            prefix_groups[prefix] = []
        prefix_groups[prefix].append(col)
    
    # Sort prefixes by number of columns (largest first)
    sorted_prefixes = sorted(prefix_groups.keys(), 
                           key=lambda x: len(prefix_groups[x]), reverse=True)
    
    groups = []
    current_group = []
    
    for prefix in sorted_prefixes:
        prefix_columns = prefix_groups[prefix]
        
        # If adding this prefix would exceed max_columns, start a new group
        if len(current_group) + len(prefix_columns) > max_columns and current_group:
            groups.append(current_group)
            current_group = []
        
        # Add columns from this prefix
        current_group.extend(prefix_columns)
        
        # If current group is at max, start a new one
        if len(current_group) >= max_columns:
            groups.append(current_group)
            current_group = []
    
    # Add any remaining columns
    if current_group:
        groups.append(current_group)
    
    return groups

def get_table_split_recommendation(column_count: int) -> Dict[str, Any]:
    """
    Get recommendations for splitting a table based on column count.
    
    Args:
        column_count: Number of columns in the table
        
    Returns:
        Dictionary with recommendations
    """
    if column_count <= 50:
        return {
            "should_split": False,
            "reason": "Table size is manageable",
            "recommendation": "Use as-is"
        }
    elif column_count <= 100:
        return {
            "should_split": True,
            "reason": "Table has many columns",
            "recommendation": "Split into 2-3 tables",
            "max_columns_per_table": 40,
            "strategy": "sequential"
        }
    elif column_count <= 200:
        return {
            "should_split": True,
            "reason": "Table has very many columns",
            "recommendation": "Split into 4-6 tables",
            "max_columns_per_table": 35,
            "strategy": "grouped"
        }
    else:
        return {
            "should_split": True,
            "reason": "Table has extremely many columns",
            "recommendation": "Split into 6+ tables or consider different database design",
            "max_columns_per_table": 30,
            "strategy": "grouped"
        } 