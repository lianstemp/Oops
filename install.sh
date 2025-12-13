#!/bin/bash

# Oops Hybrid Installer - Native app + Docker sandbox

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Oops - Red Team Orchestrator Setup  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Function to check if Docker is installed
check_docker() {
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Step 1: Install native app with Poetry
echo -e "${BLUE}Step 1: Installing Oops CLI (native)...${NC}"

# Check for Poetry
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
poetry install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Oops CLI installed successfully${NC}"
else
    echo -e "${RED}✗ Failed to install Oops CLI${NC}"
    exit 1
fi

echo ""

# Step 2: Setup Docker sandbox
echo -e "${BLUE}Step 2: Setting up Docker sandbox...${NC}"

if ! check_docker; then
    echo -e "${YELLOW}⚠ Docker not found!${NC}"
    echo ""
    echo "Docker is required for isolated tool execution."
    echo "Install Docker:"
    echo "  - Ubuntu/Debian: sudo apt-get install docker.io docker-compose"
    echo "  - Fedora: sudo dnf install docker docker-compose"
    echo "  - Arch: sudo pacman -S docker docker-compose"
    echo ""
    echo "Or visit: https://docs.docker.com/get-docker/"
    echo ""
    echo -e "${YELLOW}Oops will run in LOCAL MODE (tools on host)${NC}"
else
    # Create directories
    mkdir -p output
    
    # Copy .env if it doesn't exist
    if [ ! -f .env ]; then
        echo -e "${YELLOW}Creating .env file from template...${NC}"
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Please edit .env and add your LLM_API_KEY${NC}"
    fi
    
    # Build sandbox image
    echo -e "${BLUE}Building sandbox image (this may take a few minutes)...${NC}"
    docker-compose build
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Sandbox image built successfully${NC}"
        
        # Start sandbox
        echo -e "${BLUE}Starting sandbox container...${NC}"
        docker-compose up -d
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Sandbox started successfully${NC}"
        else
            echo -e "${YELLOW}⚠ Failed to start sandbox${NC}"
        fi
    else
        echo -e "${RED}✗ Failed to build sandbox image${NC}"
        echo -e "${YELLOW}Oops will run in LOCAL MODE${NC}"
    fi
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Installation Complete!         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""

# Usage instructions
echo -e "${BLUE}Usage:${NC}"
echo "  poetry run oops"
echo ""
echo -e "${BLUE}Sandbox Management:${NC}"
echo "  Start sandbox:  docker-compose up -d"
echo "  Stop sandbox:   docker-compose down"
echo "  View logs:      docker-compose logs -f"
echo "  Rebuild:        docker-compose build --no-cache"
echo ""
echo -e "${BLUE}Tip:${NC} Add this alias to your shell configuration:"
echo "  alias oops='poetry run oops'"
echo ""
echo -e "${YELLOW}⚠️  Don't forget to configure .env with your LLM_API_KEY${NC}"
