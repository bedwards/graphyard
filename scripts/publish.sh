#!/bin/bash
# Graphyard Publish Script
# Single command to generate charts, build site, and deploy to GitHub Pages
#
# Usage: ./scripts/publish.sh [--no-push]

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "Graphyard Publish Pipeline"
echo "========================================"
echo ""

# Step 1: Generate charts with Altair
echo "[1/4] Generating charts..."
cd "$PROJECT_ROOT/charts"
uv run python generate_dual.py --renderer=altair 2>&1 | grep -E "(Rendering|Saved|charts generated)" || true

# Step 2: Build Astro site
echo ""
echo "[2/4] Building site..."
cd "$PROJECT_ROOT/site"
npm run build 2>&1 | grep -E "(building|built|Complete)" || true

# Step 3: Copy to docs folder for GitHub Pages
echo ""
echo "[3/4] Copying to docs/..."
rm -rf "$PROJECT_ROOT/docs"
cp -r "$PROJECT_ROOT/site/dist" "$PROJECT_ROOT/docs"

# Step 4: Git commit and push (unless --no-push)
echo ""
if [[ "$1" == "--no-push" ]]; then
    echo "[4/4] Skipping git push (--no-push flag)"
    echo ""
    echo "Changes staged. Run 'git add -A && git commit && git push' to publish."
else
    echo "[4/4] Committing and pushing..."
    cd "$PROJECT_ROOT"
    git add -A

    # Generate commit message from changes
    CHANGED_FILES=$(git diff --cached --name-only | wc -l | tr -d ' ')
    COMMIT_MSG="Update site (${CHANGED_FILES} files changed)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

    git commit -m "$COMMIT_MSG" || echo "Nothing to commit"
    git push origin main
fi

echo ""
echo "========================================"
echo "Done! Site published to:"
echo "https://bedwards.github.io/graphyard/"
echo "========================================"
