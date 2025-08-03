import subprocess
import os
import mimetypes
from pathlib import Path


def get_staged_files() -> list:
    """
    Get a list of staged files in the current git repository.

    Returns:
        list: A list of staged file paths.
    """
    try:
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'],
                                check=True,
                                text=True,
                                capture_output=True)
        files = result.stdout.strip().split('\n')
        return [file for file in files if file]  # Filter out empty strings
    except subprocess.CalledProcessError as e:
        print(f"Error while getting staged files: {e}")
        return []


def is_text_file(file_path: str) -> bool:
    """
    Check if a file is a text file that can be scanned for secrets.
    
    Args:
        file_path (str): Path to the file to check
        
    Returns:
        bool: True if the file is a text file, False otherwise
    """
    if not os.path.exists(file_path):
        return False
    
    # Get file extension
    file_ext = Path(file_path).suffix.lower()
    
    # Common text file extensions
    text_extensions = {
        '.txt', '.md', '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', 
        '.scss', '.sass', '.json', '.xml', '.yaml', '.yml', '.toml', '.ini',
        '.cfg', '.conf', '.config', '.env', '.properties', '.sh', '.bash',
        '.zsh', '.fish', '.ps1', '.bat', '.cmd', '.sql', '.r', '.rb', '.php',
        '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.go', '.rs', '.swift',
        '.kt', '.scala', '.clj', '.hs', '.ml', '.fs', '.vb', '.pl', '.pm',
        '.tcl', '.lua', '.vim', '.tex', '.rst', '.adoc', '.wiki', '.log',
        '.csv', '.tsv', '.tab', '.dat', '.asc', '.pem', '.key', '.crt',
        '.cer', '.der', '.p12', '.pfx', '.p7b', '.p7c', '.crl', '.csr'
    }
    
    # Check if it's a known text extension
    if file_ext in text_extensions:
        return True
    
    # For files without extension or unknown extensions, try to detect MIME type
    try:
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type and mime_type.startswith('text/'):
            return True
        
        # Additional check for binary files
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            # Check if the chunk contains null bytes (indicates binary)
            if b'\x00' in chunk:
                return False
            # Check if it's mostly printable ASCII
            try:
                chunk.decode('utf-8')
                return True
            except UnicodeDecodeError:
                return False
    except (OSError, IOError):
        return False
    
    return True


def get_scannable_staged_files() -> list:
    """
    Get a list of staged files that can be scanned for secrets.
    
    Returns:
        list: A list of staged file paths that are text files.
    """
    staged_files = get_staged_files()
    scannable_files = []
    
    for file_path in staged_files:
        if is_text_file(file_path):
            scannable_files.append(file_path)
    
    return scannable_files


def is_git_repository() -> bool:
    """
    Check if the current directory is a git repository.
    
    Returns:
        bool: True if it's a git repository, False otherwise
    """
    try:
        subprocess.run(['git', 'rev-parse', '--git-dir'], 
                      check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def install_git_hook() -> bool:
    """
    Install git-shield as a pre-commit hook.
    
    Returns:
        bool: True if hook was installed successfully, False otherwise
    """
    if not is_git_repository():
        print("ERROR: Not in a git repository. Please run this command from a git repository.")
        return False
    
    hook_content = """#!/bin/sh
# git-shield pre-commit hook
# This hook runs git-shield scan before each commit

# Run git-shield scan on staged files
git-shield scan --staged

# If git-shield found secrets, the commit will be blocked
if [ $? -ne 0 ]; then
    echo "Commit blocked due to detected secrets. Please remove secrets before committing."
    exit 1
fi

echo "git-shield scan passed. Proceeding with commit..."
exit 0
"""
    
    try:
        # Create .git/hooks directory if it doesn't exist
        hooks_dir = Path('.git/hooks')
        hooks_dir.mkdir(parents=True, exist_ok=True)
        
        # Write the pre-commit hook
        hook_file = hooks_dir / 'pre-commit'
        with open(hook_file, 'w', encoding='utf-8') as f:
            f.write(hook_content)
        
        # Make the hook executable
        os.chmod(hook_file, 0o755)
        
        print("SUCCESS: git-shield pre-commit hook installed successfully!")
        print("   The hook will now automatically scan for secrets before each commit.")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to install git hook: {e}")
        return False


def uninstall_git_hook() -> bool:
    """
    Uninstall git-shield pre-commit hook.
    
    Returns:
        bool: True if hook was uninstalled successfully, False otherwise
    """
    hook_file = Path('.git/hooks/pre-commit')
    
    if not hook_file.exists():
        print("INFO: No git-shield pre-commit hook found.")
        return True
    
    try:
        # Check if this is our hook by reading the first few lines
        with open(hook_file, 'r') as f:
            content = f.read()
        
        if 'git-shield pre-commit hook' in content:
            hook_file.unlink()
            print("SUCCESS: git-shield pre-commit hook uninstalled successfully!")
            return True
        else:
            print("INFO: Found a pre-commit hook, but it's not git-shield. Skipping removal.")
            return True
            
    except Exception as e:
        print(f"ERROR: Failed to uninstall git hook: {e}")
        return False
