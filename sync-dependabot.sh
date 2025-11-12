#!/bin/bash

# Sync dependabot configuration to a repository
# Usage: ./sync-dependabot.sh <target-repo-path> [template-name]
#
# Examples:
#   ./sync-dependabot.sh ~/code/my-repo npm
#   ./sync-dependabot.sh ~/code/my-repo github-actions
#   ./sync-dependabot.sh ~/code/my-repo  # defaults to npm

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if target repository path is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Target repository path is required${NC}"
    echo "Usage: ./sync-dependabot.sh <target-repo-path> [template-name]"
    echo ""
    echo "Available templates:"
    echo "  - npm (default)"
    echo "  - github-actions"
    exit 1
fi

TARGET_REPO="$1"
TEMPLATE="${2:-npm}"  # Default to npm if not specified
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_FILE="${SCRIPT_DIR}/templates/dependabot-${TEMPLATE}.yml"
TARGET_FILE="${TARGET_REPO}/.github/dependabot.yml"

# Validate target repository exists
if [ ! -d "$TARGET_REPO" ]; then
    echo -e "${RED}Error: Target repository does not exist: ${TARGET_REPO}${NC}"
    exit 1
fi

# Validate template exists
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo -e "${RED}Error: Template not found: dependabot-${TEMPLATE}.yml${NC}"
    echo ""
    echo "Available templates:"
    ls -1 "${SCRIPT_DIR}/templates/" | grep "dependabot-" | sed 's/dependabot-//g' | sed 's/.yml//g'
    exit 1
fi

# Create .github directory if it doesn't exist
mkdir -p "${TARGET_REPO}/.github"

# Backup existing file if it exists
if [ -f "$TARGET_FILE" ]; then
    BACKUP_FILE="${TARGET_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${YELLOW}Backing up existing dependabot.yml to: ${BACKUP_FILE}${NC}"
    cp "$TARGET_FILE" "$BACKUP_FILE"
fi

# Copy the template
echo -e "${GREEN}Copying ${TEMPLATE} template to ${TARGET_REPO}/.github/dependabot.yml${NC}"
cp "$TEMPLATE_FILE" "$TARGET_FILE"

echo -e "${GREEN}✓ Dependabot configuration synced successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Review the configuration at: ${TARGET_FILE}"
echo "2. Commit the changes to your repository"
echo "3. Push to GitHub to enable Dependabot"
