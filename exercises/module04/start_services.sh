#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   Module 3: Money Transfer System - Startup${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# PID tracking
ACCOUNT_API_PID=""
MONEY_TRANSFER_PID=""
WORKER_PID=""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"
    
    if [ ! -z "$ACCOUNT_API_PID" ]; then
        echo -e "  Stopping Account API (PID: $ACCOUNT_API_PID)..."
        kill $ACCOUNT_API_PID 2>/dev/null
    fi
    
    if [ ! -z "$MONEY_TRANSFER_PID" ]; then
        echo -e "  Stopping Money Transfer API (PID: $MONEY_TRANSFER_PID)..."
        kill $MONEY_TRANSFER_PID 2>/dev/null
    fi
    
    if [ ! -z "$WORKER_PID" ]; then
        echo -e "  Stopping Worker (PID: $WORKER_PID)..."
        kill $WORKER_PID 2>/dev/null
    fi
    
    echo -e "${GREEN}✓ All services stopped${NC}"
    exit 0
}

# Set up trap to catch SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check uv
if ! command -v uv &> /dev/null; then
    echo -e "${RED}✗ uv not found${NC}"
    echo -e "  Please install uv: https://docs.astral.sh/uv/"
    exit 1
else
    echo -e "${GREEN}✓ uv found${NC}"
fi

# Check if Temporal CLI is available (optional)
if ! command -v temporal &> /dev/null; then
    echo -e "${YELLOW}⚠ Temporal CLI not found (optional)${NC}"
else
    echo -e "${GREEN}✓ Temporal CLI found${NC}"
fi

echo ""
echo -e "${YELLOW}Starting services...${NC}"
echo ""

# Start Account API
echo -e "${BLUE}[1/3]${NC} Starting Account API on port 5000..."
uv run python account_api.py > account_api.log 2>&1 &
ACCOUNT_API_PID=$!
sleep 2

# Check if Account API started successfully
if kill -0 $ACCOUNT_API_PID 2>/dev/null; then
    echo -e "${GREEN}✓ Account API started (PID: $ACCOUNT_API_PID)${NC}"
else
    echo -e "${RED}✗ Failed to start Account API${NC}"
    echo -e "  Check account_api.log for errors"
    exit 1
fi

# Start Money Transfer API (in background)
echo -e "${BLUE}[2/3]${NC} Starting Money Transfer API on port 5001..."
uv run python money_transfer_api.py > money_transfer_api.log 2>&1 &
MONEY_TRANSFER_PID=$!
sleep 2

# Check if Money Transfer API started successfully
if kill -0 $MONEY_TRANSFER_PID 2>/dev/null; then
    echo -e "${GREEN}✓ Money Transfer API started (PID: $MONEY_TRANSFER_PID)${NC}"
else
    echo -e "${RED}✗ Failed to start Money Transfer API${NC}"
    echo -e "  Check money_transfer_api.log for errors"
    cleanup
    exit 1
fi

# Start Worker (in foreground)
echo -e "${BLUE}[3/3]${NC} Starting Temporal Worker..."
echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}✓ All services started successfully!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${BLUE}🌐 Open your browser to:${NC}"
echo -e "   ${YELLOW}http://localhost:5001/${NC}"
echo ""
echo -e "${BLUE}📋 Prerequisites:${NC}"
echo -e "   • Temporal server must be running on localhost:7233"
echo -e "   • Run: ${YELLOW}temporal server start-dev${NC}"
echo ""
echo -e "${BLUE}📝 Service logs:${NC}"
echo -e "   • Account API: account_api.log"
echo -e "   • Money Transfer API: money_transfer_api.log"
echo -e "   • Worker: output below"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""

# Run Worker in foreground (this will show logs)
uv run python worker.py

# If Worker exits, cleanup
cleanup
