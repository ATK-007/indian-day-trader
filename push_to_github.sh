#!/usr/bin/env bash
# ==============================================================================
# push_to_github.sh
# Push Indian Day Trader skills to your personal GitHub repository.
# ==============================================================================

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

echo "======================================================================"
echo "🇮🇳  Indian Day Trader — Push to GitHub"
echo "======================================================================"

# Check if git is available
if ! command -v git &> /dev/null || ! git --version &> /dev/null; then
    echo "[!] Git command-line tools are not yet active on your Mac."
    echo "    Running 'xcode-select --install'..."
    xcode-select --install || true
    echo ""
    echo "Please click 'Install' on the Apple dialog, wait 1-2 minutes for completion, then re-run this script."
    exit 1
fi

echo "[✓] Git is installed: $(git --version)"

# Check if git repo is already initialized
if [ ! -d ".git" ]; then
    echo "[*] Initializing git repository..."
    git init
    git branch -M main
else
    echo "[✓] Git repository already initialized."
fi

# Configure git identity if not set
if [ -z "$(git config user.name)" ]; then
    read -p "Enter your GitHub display name (e.g. Aditya Atmakuri): " GH_NAME
    git config user.name "$GH_NAME"
fi

if [ -z "$(git config user.email)" ]; then
    read -p "Enter your GitHub email address: " GH_EMAIL
    git config user.email "$GH_EMAIL"
fi

echo "[*] Staging all files..."
git add .

echo "[*] Committing files..."
git commit -m "Initial commit: 11 Indian Day Trader skills for NSE/BSE" || echo "Nothing new to commit."

# Ask for GitHub remote repository URL if not configured
CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null || true)

if [ -z "$CURRENT_REMOTE" ]; then
    echo ""
    echo "----------------------------------------------------------------------"
    echo "Create a new repository on GitHub (https://github.com/new):"
    echo "  1. Repository name: indian-day-trader (or day-trader-skill-india)"
    echo "  2. Leave 'Initialize with README' UNCHECKED (we already have one)."
    echo "  3. Click 'Create repository'."
    echo "----------------------------------------------------------------------"
    echo ""
    read -p "Enter your GitHub repository URL (e.g. https://github.com/USERNAME/indian-day-trader.git): " REPO_URL

    if [ -n "$REPO_URL" ]; then
        git remote add origin "$REPO_URL"
    else
        echo "[!] No URL provided. You can add it later using:"
        echo "    git remote add origin https://github.com/USERNAME/indian-day-trader.git"
        echo "    git push -u origin main"
        exit 0
    fi
else
    echo "[✓] Existing remote origin found: $CURRENT_REMOTE"
fi

echo "[*] Pushing to GitHub (main branch)..."
git push -u origin main

echo ""
echo "======================================================================"
echo "[SUCCESS] All 11 Indian Day Trader skills are live on your GitHub!"
echo "======================================================================"
