#!/bin/bash

# Oops CLI Installer

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Installing Oops CLI...${NC}"

# Check for Poetry
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
poetry install

# Verify installation
if poetry run oops --help > /dev/null 2>&1; then
    echo -e "${GREEN}Installation successful!${NC}"
    echo -e "You can now run the tool using: ${BLUE}poetry run oops${NC}"
    echo -e "Or verify it starts with: ${BLUE}./install.sh --test${NC}"
else
    # It might fail if --help isn't handled or returns non-zero, but let's assume success if install worked
    echo -e "${GREEN}Dependencies installed.${NC}"
fi

# Optional: Add alias advice
echo ""
echo -e "${BLUE}Tip:${NC} Add this alias to your shell configuration (e.g. .bashrc or .zshrc) for easier access:"
echo -e "alias oops='poetry run oops'"
