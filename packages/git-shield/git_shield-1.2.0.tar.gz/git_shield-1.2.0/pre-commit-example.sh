#!/bin/sh
# git-shield pre-commit hook example
# This is an example of how to set up git-shield as a pre-commit hook

# Run git-shield scan on staged files
echo "🔍 Running git-shield scan on staged files..."
git-shield scan --staged

# If git-shield found secrets, the commit will be blocked
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Commit blocked due to detected secrets!"
    echo "   Please remove the secrets from your files before committing."
    echo "   You can run 'git-shield scan --staged' to see the details."
    exit 1
fi

echo "✅ git-shield scan passed. Proceeding with commit..."
exit 0
