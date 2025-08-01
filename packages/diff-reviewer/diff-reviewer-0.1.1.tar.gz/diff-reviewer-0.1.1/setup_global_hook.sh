# setup_global_hook.sh
#!/bin/bash

echo "🔧 Setting up global pre-commit hook..."

HOOK_PATH="$HOME/.global-git-hooks"

mkdir -p "$HOOK_PATH"
cp hooks/pre-commit "$HOOK_PATH/pre-commit"
chmod +x "$HOOK_PATH/pre-commit"

git config --global core.hooksPath "$HOOK_PATH"

echo "✅ Global Git hook installed!"
