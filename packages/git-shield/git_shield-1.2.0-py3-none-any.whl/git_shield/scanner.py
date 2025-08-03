import re
import os
from .utils import is_text_file


def scan_line_for_secrets(line: str, compiled_patterns: dict) -> list:
    """
    Scan a single line for secrets using compiled regex patterns.

    Args:
        line (str): The line of text to scan.
        compiled_patterns (dict): A dictionary of compiled regex patterns.

    Returns:
        list: A list of found secrets in the line.
    """
    findings = []
    for pattern_name, regex in compiled_patterns.items():
        match = regex.search(line)
        if match:
            findings.append({
                "pattern": pattern_name,
                "match": match.group()
            })
    return findings


def scan_file_for_secrets(file_path: str, compiled_patterns: dict) -> list:
    """
    Scan a file line by line for secrets using compiled regex patterns.

    Args:
        file_path (str): The path to the file to scan.
        compiled_patterns (dict): A dictionary of compiled regex patterns.

    Returns:
        list: A list of findings, each containing the pattern and matched secret.
    """
    file_findings = []

    # Check if file exists and is readable
    if not os.path.exists(file_path):
        print(f"WARNING: File {file_path} does not exist")
        return file_findings

    # Skip patterns.py file as it contains regex patterns that trigger false positives
    if file_path.endswith('patterns.py') or 'patterns.py' in file_path:
        print(f"INFO: Skipping patterns.py file to avoid false positives")
        return file_findings

    # Check if file is a text file that can be scanned
    if not is_text_file(file_path):
        print(f"INFO: Skipping binary file: {file_path}")
        return file_findings

    try:
        # Try to read the file with UTF-8 encoding first
        with open(file_path, 'r', encoding='utf-8') as file:
            for idx, line in enumerate(file, 1):
                line_findings = scan_line_for_secrets(line, compiled_patterns)
                
                for finding in line_findings:
                    file_findings.append({
                        "file": file_path,
                        "line_number": idx,
                        "pattern": finding["pattern"],
                        "match": finding["match"],
                        "code": line.strip()
                    })
    except UnicodeDecodeError:
        # If UTF-8 fails, try with different encodings
        encodings = ['latin-1', 'cp1252', 'iso-8859-1']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    for idx, line in enumerate(file, 1):
                        line_findings = scan_line_for_secrets(line, compiled_patterns)
                        
                        for finding in line_findings:
                            file_findings.append({
                                "file": file_path,
                                "line_number": idx,
                                "pattern": finding["pattern"],
                                "match": finding["match"],
                                "code": line.strip()
                            })
                break  # If successful, break out of encoding loop
            except UnicodeDecodeError:
                continue
        else:
            print(f"WARNING: Could not read file {file_path} with any supported encoding")
    except PermissionError:
        print(f"WARNING: Permission denied reading file {file_path}")
    except Exception as e:
        print(f"WARNING: Error reading file {file_path}: {e}")

    return file_findings


def scan_files_for_secrets(file_paths: list, compiled_patterns: dict) -> list:
    """
    Scan multiple files for secrets.

    Args:
        file_paths (list): List of file paths to scan.
        compiled_patterns (dict): A dictionary of compiled regex patterns.

    Returns:
        list: A list of all findings from all files.
    """
    all_findings = []
    
    for file_path in file_paths:
        file_findings = scan_file_for_secrets(file_path, compiled_patterns)
        all_findings.extend(file_findings)
    
    return all_findings
