#!/usr/bin/env bash
# Create IdleHunter repo on GitHub and push (requires GitHub CLI: gh auth login).
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

REPO_NAME="IdleHunter"

if ! command -v gh &>/dev/null; then
  echo "GitHub CLI (gh) is not installed."
  echo "Install: https://cli.github.com/ (e.g. apt install gh  or  brew install gh)"
  echo "Then run: gh auth login"
  echo "Then run this script again: ./scripts/github-create-and-push.sh"
  exit 1
fi

if ! gh auth status &>/dev/null; then
  echo "Not logged in to GitHub. Run: gh auth login"
  exit 1
fi

# Create repo if it doesn't exist on GitHub
LOGIN=$(gh api user -q .login 2>/dev/null)
REPO_URL="https://github.com/${LOGIN}/${REPO_NAME}.git"
if ! git remote get-url origin 2>/dev/null | grep -q muratbulat/IdleHunter; then
  echo "Creating GitHub repository $REPO_NAME..."
  gh repo create "$REPO_NAME" --public --description "Detect idle/zombie VMs across vCenter, Aria, Stor2RRD" || true
  git remote set-url origin "$REPO_URL"
fi
echo "Pushing to origin main..."
git push -u origin main
echo "Done. Your repo: $REPO_URL"
