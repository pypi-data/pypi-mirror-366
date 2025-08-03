# Changelog

## [1.1.0] - 2024-01-XX

### Added
- **Smart File Type Detection**: Automatically detects and scans text files including:
  - Code files (`.py`, `.js`, `.ts`, `.java`, `.cpp`, etc.)
  - Configuration files (`.env`, `.config`, `.yml`, `.json`, etc.)
  - Documentation (`.md`, `.txt`, `.rst`, etc.)
  - Certificate files (`.pem`, `.key`, `.crt`, etc.)
  - And many more supported formats

- **Git Hook Management Commands**:
  - `git-shield install` - Install pre-commit hook
  - `git-shield uninstall` - Uninstall pre-commit hook
  - `git-shield status` - Check hook installation status

- **Enhanced CLI Commands**:
  - `git-shield scan --staged` - Scan staged files
  - `git-shield scan --files file1.txt file2.py` - Scan specific files
  - Better error messages and user guidance

- **Comprehensive Secret Detection Patterns**:
  - AWS Access Keys & Secret Keys
  - Private/Public Keys (RSA, DSA, EC, SSH)
  - API Keys (GitHub, Google, Stripe, Twilio, etc.)
  - Database URLs (PostgreSQL, MongoDB, Redis, MySQL)
  - OAuth tokens and client secrets
  - JWT tokens
  - Slack tokens and webhooks
  - Environment variables
  - Secrets in comments

### Fixed
- **File Type Detection**: Now properly detects and scans `.txt` files and other text formats
- **Git Hook Integration**: Automatic scanning before commits with proper blocking
- **Encoding Issues**: Fixed Unicode/emoji character issues on Windows systems
- **Pattern Optimization**: Reduced false positives and duplicate detections
- **Error Handling**: Improved error messages and exception handling

### Changed
- **Version**: Updated from 1.0.0 to 1.1.0
- **Development Status**: Changed from Production/Stable to Beta
- **CLI Output**: Removed emoji characters for better Windows compatibility
- **Pattern Matching**: More specific patterns to reduce false positives

### Security
- **Automatic Blocking**: Commits are now automatically blocked when secrets are detected
- **Pre-commit Hooks**: Integrated git hooks for seamless protection
- **Comprehensive Coverage**: Enhanced pattern library for better secret detection

## [1.0.0] - Initial Release

### Features
- Basic secret detection using regex patterns
- Staged file scanning
- Simple CLI interface
- Basic git hook support 