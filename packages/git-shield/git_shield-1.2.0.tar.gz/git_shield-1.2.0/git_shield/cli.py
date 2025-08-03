import sys
import click
from .patterns import load_patterns
from .scanner import scan_files_for_secrets
from .utils import get_scannable_staged_files, install_git_hook, uninstall_git_hook, is_git_repository


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    git-shield: Advanced secret detection for git repositories.
    """
    pass


@cli.command()
@click.option('--staged', is_flag=True, help='Scan staged files for secrets')
@click.option('--files', multiple=True, help='Specific files to scan')
def scan(staged, files):
    """
    Scan files for potential secrets.
    """
    if not staged and not files:
        print("ERROR: Please specify either --staged to scan staged files or --files to scan specific files")
        print("   Example: git-shield scan --staged")
        print("   Example: git-shield scan --files file1.txt file2.py")
        sys.exit(2)

    files_to_scan = []
    
    if staged:
        if not is_git_repository():
            print("ERROR: Not in a git repository. Please run this command from a git repository.")
            sys.exit(2)
        
        try:
            files_to_scan = get_scannable_staged_files()
        except Exception as e:
            print(f"ERROR: Could not get staged files: {e}")
            sys.exit(2)
    
    if files:
        files_to_scan.extend(files)
    
    # Remove duplicates while preserving order
    files_to_scan = list(dict.fromkeys(files_to_scan))
    
    if not files_to_scan:
        print("SUCCESS: No files to scan")
        sys.exit(0)

    try:
        compiled_patterns = load_patterns()
        if not compiled_patterns:
            print(f"ERROR: Problem loading patterns (zero patterns found)")
            sys.exit(2)
    except Exception as e:
        print(f"ERROR: Problem loading patterns: {e}")
        sys.exit(2)

    print(f"Scanning {len(files_to_scan)} file(s) for secrets...")
    
    findings = scan_files_for_secrets(files_to_scan, compiled_patterns)

    if findings:
        print(f"\nSECRETS DETECTED:")
        for result in findings:
            masked = result['match'][:4] + \
                '*' * max(0, len(result['match']) - 4)
            print(
                f"   File: {result['file']}:{result['line_number']} [{result['pattern']}] -> {masked}")
            print(f"      Code: {result['code']}")
            print()

        print(f"BLOCKED: Found {len(findings)} secret(s). Please remove them before committing.")
        sys.exit(1)
    else:
        print(f"SUCCESS: No secrets detected. Safe to commit.")
        sys.exit(0)


@cli.command()
def install():
    """
    Install git-shield as a pre-commit hook.
    """
    if install_git_hook():
        sys.exit(0)
    else:
        sys.exit(1)


@cli.command()
def uninstall():
    """
    Uninstall git-shield pre-commit hook.
    """
    if uninstall_git_hook():
        sys.exit(0)
    else:
        sys.exit(1)


@cli.command()
def status():
    """
    Check git-shield installation status.
    """
    if not is_git_repository():
        print("ERROR: Not in a git repository")
        sys.exit(1)
    
    from pathlib import Path
    hook_file = Path('.git/hooks/pre-commit')
    
    if hook_file.exists():
        try:
            with open(hook_file, 'r') as f:
                content = f.read()
            
            if 'git-shield pre-commit hook' in content:
                print("SUCCESS: git-shield pre-commit hook is installed")
                print("   The hook will automatically scan for secrets before each commit")
            else:
                print("WARNING: A pre-commit hook exists, but it's not git-shield")
        except Exception as e:
            print(f"WARNING: Could not read pre-commit hook: {e}")
    else:
        print("ERROR: git-shield pre-commit hook is not installed")
        print("   Run 'git-shield install' to install the hook")


if __name__ == '__main__':
    cli()
