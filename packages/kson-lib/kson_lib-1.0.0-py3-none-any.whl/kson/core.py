import json
import re
import os
import sys
import traceback
from typing import Any, Union, TextIO, Dict

def _print_error(message: str, file_path: str = None, line_num: int = None, code_snippet: str = None):
    print("\n" + "="*80, file=sys.stderr)
    print(" KSON ERROR ".center(80, "!"), file=sys.stderr)
    print("="*80 + "\n", file=sys.stderr)
    
    if file_path:
        print(f"File: {file_path}", file=sys.stderr)
    if line_num is not None:
        print(f"Line: {line_num}", file=sys.stderr)
    if code_snippet:
        print("\nCode snippet:", file=sys.stderr)
        print(code_snippet, file=sys.stderr)
        print("^" * len(code_snippet.split('\n')[-1]), file=sys.stderr)
    
    print(f"\nError: {message}\n", file=sys.stderr)
    print("="*80 + "\n", file=sys.stderr)

def _validate_file_extension(file_path: str) -> None:
    if not file_path.endswith('.kson'):
        raise ValueError("File must have a .kson extension")

def _remove_comments(json_str: str) -> str:
    pattern = r'\/\/.*?$|\/\*[\s\S]*?\*\/'
    cleaned = re.sub(pattern, '', json_str, flags=re.MULTILINE)
    return cleaned.strip()

def loads(json_str: str, **kwargs) -> Any:
    try:
        cleaned = _remove_comments(json_str)
        return json.loads(cleaned, **kwargs)
    except json.JSONDecodeError as e:
        error_msg = str(e)
        line_num = None
        col_num = None
        code_snippet = None
        
        if "line" in error_msg and "column" in error_msg:
            parts = error_msg.split(":")
            if len(parts) >= 3:
                line_part = parts[1].strip()
                col_part = parts[2].split(" ")[0].strip()
                try:
                    line_num = int(line_part.split(" ")[1])
                    col_num = int(col_part)
                except (ValueError, IndexError):
                    pass
        
        if line_num is not None:
            lines = json_str.split('\n')
            if line_num <= len(lines):
                code_snippet = lines[line_num-1]
        
        custom_msg = f"Invalid KSON format"
        if line_num is not None and col_num is not None:
            custom_msg += f" at line {line_num}, column {col_num}"
        
        _print_error(custom_msg, line_num=line_num, code_snippet=code_snippet)
        raise ValueError(custom_msg) from None
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_list = traceback.extract_tb(exc_traceback)
        
        relevant_frame = None
        for frame in reversed(tb_list):
            if frame.filename.endswith('core.py'):
                relevant_frame = frame
                break
        
        if relevant_frame:
            line_num = relevant_frame.lineno
            with open(relevant_frame.filename, 'r') as f:
                lines = f.readlines()
                if line_num <= len(lines):
                    code_snippet = lines[line_num-1].strip()
            
            _print_error(str(e), file_path=relevant_frame.filename, 
                        line_num=line_num, code_snippet=code_snippet)
        
        raise ValueError(f"KSON processing error: {str(e)}") from None

def load(fp: Union[TextIO, str], **kwargs) -> Any:
    try:
        if isinstance(fp, str):
            _validate_file_extension(fp)
            with open(fp, 'r') as file:
                content = file.read()
                return loads(content, **kwargs)
        else:
            content = fp.read()
            return loads(content, **kwargs)
    except Exception as e:
        if isinstance(e, ValueError) and str(e).startswith("File must have"):
            _print_error(str(e))
        raise

def dumps(obj: Any, **kwargs) -> str:
    try:
        return json.dumps(obj, **kwargs)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        _print_error(f"Failed to serialize object to KSON: {str(e)}")
        raise ValueError(f"KSON serialization error: {str(e)}") from None

def dump(obj: Any, fp: Union[TextIO, str], **kwargs) -> None:
    try:
        if isinstance(fp, str):
            _validate_file_extension(fp)
            with open(fp, 'w') as file:
                json.dump(obj, file, **kwargs)
        else:
            json.dump(obj, fp, **kwargs)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        _print_error(f"Failed to write KSON: {str(e)}")
        raise ValueError(f"KSON write error: {str(e)}") from None