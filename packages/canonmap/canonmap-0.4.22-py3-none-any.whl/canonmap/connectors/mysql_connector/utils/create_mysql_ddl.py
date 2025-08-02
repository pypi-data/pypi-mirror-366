# canonmap/services/database/mysql/utils/create_mysql_ddl.py

import re
from pathlib import Path
from decimal import Decimal
from typing import Union

import pandas as pd

from canonmap.connectors.mysql_connector.managers.database_manager.validators.responses import CreateDDLResponse
from canonmap.connectors.mysql_connector.managers.table_manager.utils._clean_field_names import clean_field_names

def estimate_row_size(column_defs: list) -> int:
    """
    Estimate the row size in bytes for the given column definitions.
    
    Args:
        column_defs: List of column definition strings
        
    Returns:
        int: Estimated row size in bytes
    """
    total_size = 0
    for col_def in column_defs:
        col_type = col_def.split()[1].upper()  # Extract type from "`name` TYPE"
        
        if col_type.startswith('VARCHAR'):
            # Extract length from VARCHAR(n)
            length = int(col_type.split('(')[1].split(')')[0])
            # VARCHAR uses 1-2 bytes for length + actual data
            total_size += 2 + length
        elif col_type == 'TEXT':
            total_size += 2 + 65535  # TEXT uses 2 bytes for length + max 65535 bytes
        elif col_type == 'MEDIUMTEXT':
            total_size += 3 + 16777215  # MEDIUMTEXT uses 3 bytes for length + max 16777215 bytes
        elif col_type == 'LONGTEXT':
            total_size += 4 + 4294967295  # LONGTEXT uses 4 bytes for length + max 4294967295 bytes
        elif col_type in ['TINYINT', 'TINYINT(1)']:
            total_size += 1
        elif col_type in ['SMALLINT', 'SMALLINT UNSIGNED']:
            total_size += 2
        elif col_type in ['INT', 'INT UNSIGNED', 'MEDIUMINT', 'MEDIUMINT UNSIGNED']:
            total_size += 4
        elif col_type in ['BIGINT', 'BIGINT UNSIGNED']:
            total_size += 8
        elif col_type.startswith('DECIMAL'):
            # DECIMAL uses 4 bytes per 9 digits
            precision = int(col_type.split('(')[1].split(',')[0])
            total_size += (precision // 9 + 1) * 4
        elif col_type in ['FLOAT']:
            total_size += 4
        elif col_type in ['DOUBLE']:
            total_size += 8
        elif col_type in ['DATE']:
            total_size += 3
        elif col_type in ['TIME']:
            total_size += 3
        elif col_type in ['DATETIME', 'TIMESTAMP']:
            total_size += 8
        elif col_type in ['YEAR']:
            total_size += 1
        else:
            # Default estimate for unknown types
            total_size += 255
    
    return total_size

def optimize_column_types(column_defs: list, max_row_size: int = 8000) -> list:
    """
    Optimize column types to stay within row size limits.
    
    Args:
        column_defs: List of column definition strings
        max_row_size: Maximum allowed row size in bytes
        
    Returns:
        list: Optimized column definitions
    """
    optimized_defs = column_defs.copy()
    
    # First pass: convert VARCHAR to TEXT for long strings
    for i, col_def in enumerate(optimized_defs):
        if 'VARCHAR(' in col_def:
            # Extract length from VARCHAR(n)
            length = int(col_def.split('VARCHAR(')[1].split(')')[0])
            if length > 100:  # Convert long VARCHAR to TEXT
                col_name = col_def.split()[0]
                optimized_defs[i] = f"{col_name} TEXT"
    
    # Second pass: if still too large, convert more VARCHAR to TEXT
    estimated_size = estimate_row_size(optimized_defs)
    if estimated_size > max_row_size:
        for i, col_def in enumerate(optimized_defs):
            if 'VARCHAR(' in col_def:
                col_name = col_def.split()[0]
                optimized_defs[i] = f"{col_name} TEXT"
                estimated_size = estimate_row_size(optimized_defs)
                if estimated_size <= max_row_size:
                    break
    
    return optimized_defs

def create_mysql_ddl(table_name: str, data: Union[str, pd.DataFrame, list, Path], save_dir=None):
    """
    Generate a MySQL CREATE TABLE DDL statement from various data sources.
    
    Parameters:
        table_name (str): Desired table name (will be cleaned for MySQL).
        data: Path to a CSV file, a file-like object, a pandas DataFrame, a list of dicts, or a JSON string representing records.
        save_dir (str or Path, optional): File path to save the DDL statement.
    
    Returns:
        str: The CREATE TABLE statement corresponding to the data’s schema.
    """
    import json
    from pathlib import Path

    # Determine DataFrame source
    if isinstance(data, pd.DataFrame):
        df = data.copy()
    elif isinstance(data, list):
        df = pd.DataFrame(data)
    elif isinstance(data, str):
        # try JSON string first
        try:
            parsed = json.loads(data)
            if isinstance(parsed, list):
                df = pd.DataFrame(parsed)
            else:
                raise ValueError
        except Exception:
            # treat as CSV path
            df = pd.read_csv(
                data,
                dtype=str,
                keep_default_na=False,
                na_values=[],
                engine='python',
                on_bad_lines='skip'
            )
    elif hasattr(data, 'read'):
        df = pd.read_csv(
            data,
            dtype=str,
            keep_default_na=False,
            na_values=[],
            engine='python',
            on_bad_lines='skip'
        )
    else:
        raise ValueError("`data` must be a pandas DataFrame, list of dicts, JSON string, or path/buffer to a CSV file.")
    
    # Clean table name to be a valid MySQL identifier
    table = table_name.strip()
    table = re.sub(r'[^0-9A-Za-z_]', '_', table)            # replace invalid chars with _
    if table == '' or table.isdigit() or re.match(r'^\d', table):
        table = 'tbl_' + table                              # prefix if starts with digit or is empty
    table = table.lower()
    # Avoid reserved word conflict
    mysql_reserved = {
        "add","all","alter","analyze","and","as","asc","between","by","create","delete","desc","distinct",
        "drop","exists","from","group","having","in","index","insert","into","join","key","like","limit",
        "not","null","on","or","order","outer","select","set","table","update","union","where"
    }
    if table in mysql_reserved:
        table += "_tbl"
    if len(table) > 64:
        table = table[:64]
    
    # Clean column names using the helper function
    col_name_map = clean_field_names(df.columns.tolist())
    
    # Prepare a list for column definitions
    column_defs = []
    # Define placeholders that indicate missing data
    missing_values = {"", None, "NULL", "null", "NA", "na", "N/A", "n/a"}
    
    for col in df.columns:
        clean_name = col_name_map[col]
        values = df[col].tolist()
        # Filter out missing placeholders for type inference
        non_null_vals = [v for v in values if v not in missing_values]
        if not non_null_vals:
            # If column is entirely empty, default to TEXT (could also be VARCHAR(1) as minimal)
            col_type = "TEXT"
        else:
            # Check for booleans (true/false, yes/no, 0/1)
            val_set = {str(v).strip().lower() for v in non_null_vals}
            boolean_vals = {"true", "false", "t", "f", "yes", "no", "y", "n", "0", "1"}
            if val_set <= boolean_vals:
                col_type = "TINYINT(1)"  # MySQL boolean
            else:
                # Check if all values are numeric (int or float) or can be numeric
                all_numeric = True
                is_integer = True
                min_val = None
                max_val = None
                max_int_digits = 0
                max_frac_digits = 0
                for val in non_null_vals:
                    s = str(val).strip()
                    # General number (int/float) regex
                    if not re.fullmatch(r'-?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', s):
                        all_numeric = False
                        break
                    # If matches, determine if it has a fractional part or exponent
                    if re.fullmatch(r'-?\d+', s):
                        # pure integer string
                        n = int(s)
                        # track min/max for range
                        if min_val is None or n < min_val: 
                            min_val = n
                        if max_val is None or n > max_val: 
                            max_val = n
                        # count significant digits of integer
                        int_len = len(s.lstrip('-').lstrip('0')) or 1
                        if int_len > max_int_digits:
                            max_int_digits = int_len
                    else:
                        # number with decimal point or exponent
                        is_integer = False
                        try:
                            dec = Decimal(s)
                        except Exception:
                            dec = Decimal(str(float(s)))  # fallback to float if Decimal fails
                        # Convert to normalized string without scientific notation
                        dec_str = format(dec, 'f')
                        if dec_str.startswith('-'):
                            dec_str = dec_str[1:]
                        if '.' in dec_str:
                            int_part, frac_part = dec_str.split('.')
                        else:
                            int_part, frac_part = dec_str, ''
                        # Count digits in int and frac parts (ignore trailing zeros in fraction)
                        int_part = int_part.lstrip('0')
                        int_len = len(int_part) if int_part != '' else 0
                        frac_len = len(frac_part.rstrip('0'))
                        if int_len == 0 and frac_len == 0:
                            # value is 0.0 or 0.000... 
                            int_len = 1
                        if int_len > max_int_digits:
                            max_int_digits = int_len
                        if frac_len > max_frac_digits:
                            max_frac_digits = frac_len
                        # track min/max as floats (for range if needed)
                        try:
                            n = float(dec)
                        except Exception:
                            n = None
                        if n is not None:
                            if min_val is None or n < min_val:
                                min_val = n
                            if max_val is None or n > max_val:
                                max_val = n
                if all_numeric:
                    # If numeric, decide between int vs decimal
                    if is_integer:
                        # Choose appropriate integer type based on range
                        signed = True
                        if min_val is not None and min_val >= 0:
                            signed = False
                        if signed:
                            # use smallest signed type that fits min_val...max_val
                            if min_val is not None and max_val is not None:
                                if min_val >= -128 and max_val <= 127:
                                    col_type = "TINYINT"
                                elif min_val >= -32768 and max_val <= 32767:
                                    col_type = "SMALLINT"
                                elif min_val >= -8388608 and max_val <= 8388607:
                                    col_type = "MEDIUMINT"
                                elif min_val >= -2147483648 and max_val <= 2147483647:
                                    col_type = "INT"
                                elif min_val >= -9223372036854775808 and max_val <= 9223372036854775807:
                                    col_type = "BIGINT"
                                else:
                                    # If out of BIGINT range, use DECIMAL with all digits
                                    col_type = f"DECIMAL({max_int_digits},0)"
                            else:
                                col_type = "INT"
                        else:
                            # all values >= 0, use unsigned types
                            if max_val is not None:
                                if max_val <= 255:
                                    col_type = "TINYINT UNSIGNED"
                                elif max_val <= 65535:
                                    col_type = "SMALLINT UNSIGNED"
                                elif max_val <= 16777215:
                                    col_type = "MEDIUMINT UNSIGNED"
                                elif max_val <= 4294967295:
                                    col_type = "INT UNSIGNED"
                                elif max_val <= 18446744073709551615:
                                    col_type = "BIGINT UNSIGNED"
                                else:
                                    col_type = f"DECIMAL({max_int_digits},0)"
                            else:
                                col_type = "INT UNSIGNED"
                    else:
                        # Numeric column with a decimal part or very large/small values
                        if max_frac_digits == 0:
                            # (This case: all_numeric true, but is_integer false could happen if scientific notation of an int)
                            # Treat as integer range in such rare case
                            col_type = "INT"  # (fallback, though we could refine similar to above int logic)
                        else:
                            # Use DECIMAL for exact representation of floats
                            precision = max_int_digits + max_frac_digits
                            if precision > 65:
                                # Too many digits for DECIMAL, use floating type
                                col_type = "DOUBLE"
                            else:
                                scale = max_frac_digits
                                col_type = f"DECIMAL({precision},{scale})"
                else:
                    # Not all values are numeric – treat as text
                    max_len = max(len(str(v)) for v in non_null_vals)
                    # Be more conservative to avoid row size issues
                    if max_len <= 100:  # Reduced from 255 to be safer
                        col_type = f"VARCHAR({max_len})"
                    else:
                        # Use TEXT for longer strings to avoid row size issues
                        col_type = "TEXT"
        # Append the column definition
        column_defs.append(f"  `{clean_name}` {col_type}")
    
    # Optimize column types to avoid row size issues
    optimized_column_defs = optimize_column_types(column_defs)
    
    # Log the optimization if changes were made
    if optimized_column_defs != column_defs:
        print(f"Warning: Column types optimized to avoid row size issues for table '{table}'")
    
    # Construct the CREATE TABLE statement
    ddl = "CREATE TABLE `{}` (\n".format(table)
    ddl += ",\n".join(optimized_column_defs)
    ddl += "\n);"
    
    # Save to file if requested
    if save_dir:
        with open(save_dir, 'w') as f:
            f.write(ddl)

    return CreateDDLResponse(ddl=ddl, ddl_path=save_dir)