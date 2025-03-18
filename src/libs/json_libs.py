"""
JSON utility functions for loading, parsing, and manipulating JSON data.
"""

import json
import os

def load_json_file(file_path, encoding='utf-8', verbose=False):
    """
    Load and parse a JSON file with specified encoding.
    
    Args:
        file_path: Path to the JSON file
        encoding: File encoding (default: 'utf-8')
        verbose: Whether to print detailed information
        
    Returns:
        Parsed JSON data as Python object, or None if parsing fails
    """
    try:
        if verbose:
            print(f"Loading JSON file: {file_path}")
        
        with open(file_path, 'r', encoding=encoding) as f:
            data = json.load(f)
            
        if verbose:
            print(f"Successfully loaded JSON from {file_path}")
            
        return data
    except json.JSONDecodeError as e:
        print(f"JSON parsing error in {file_path}: {str(e)}")
        return None
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {str(e)}")
        return None

def save_json_file(data, file_path, encoding='utf-8', indent=2, verbose=False):
    """
    Save Python data structure to a JSON file.
    
    Args:
        data: Python data structure to save
        file_path: Path to save the JSON file
        encoding: File encoding (default: 'utf-8')
        indent: Indentation level for pretty printing (default: 2)
        verbose: Whether to print detailed information
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        if verbose:
            print(f"Saving JSON to file: {file_path}")
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as f:
            json.dump(data, f, indent=indent)
            
        if verbose:
            print(f"Successfully saved JSON to {file_path}")
            
        return True
    except Exception as e:
        print(f"Error saving JSON file {file_path}: {str(e)}")
        return False

def load_jsonl_file(file_path, encoding='utf-8', verbose=False):
    """
    Load and parse a JSONL file (JSON Lines) with specified encoding.
    
    Args:
        file_path: Path to the JSONL file
        encoding: File encoding (default: 'utf-8')
        verbose: Whether to print detailed information
        
    Returns:
        list: List of parsed JSON objects, or empty list if parsing fails
    """
    results = []
    line_count = 0
    error_count = 0
    
    try:
        if verbose:
            print(f"Loading JSONL file: {file_path}")
        
        with open(file_path, 'r', encoding=encoding) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                    
                line_count += 1
                try:
                    data = json.loads(line)
                    results.append(data)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON at line {line_num}: {str(e)}")
                    error_count += 1
        
        if verbose:
            print(f"Loaded {len(results)} JSON objects from {file_path}")
            if error_count > 0:
                print(f"Encountered {error_count} parsing errors")
            
        return results
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except Exception as e:
        print(f"Error loading JSONL file {file_path}: {str(e)}")
        return []

def save_jsonl_file(data_list, file_path, encoding='utf-8', verbose=False):
    """
    Save a list of Python objects as a JSONL file (JSON Lines).
    
    Args:
        data_list: List of Python objects to save
        file_path: Path to save the JSONL file
        encoding: File encoding (default: 'utf-8')
        verbose: Whether to print detailed information
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        if verbose:
            print(f"Saving JSONL to file: {file_path}")
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as f:
            for item in data_list:
                f.write(json.dumps(item) + '\n')
            
        if verbose:
            print(f"Successfully saved {len(data_list)} JSON objects to {file_path}")
            
        return True
    except Exception as e:
        print(f"Error saving JSONL file {file_path}: {str(e)}")
        return False

def get_nested_value(data, key_path, default=None):
    """
    Get a value from a nested dictionary using a dot-separated path.
    
    Args:
        data: Dictionary to extract value from
        key_path: Dot-separated path to the value (e.g., 'user.address.city')
        default: Default value to return if path not found
        
    Returns:
        The value at the specified path, or default if not found
    """
    keys = key_path.split('.')
    result = data
    
    for key in keys:
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            return default
            
    return result
