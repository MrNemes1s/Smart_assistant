#!/bin/bash
# Setup script for Python Analysis Agent

set -e

echo "================================================================"
echo "Python Analysis Agent - Setup Script"
echo "================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Docker
echo "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not found${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo -e "${RED}✗ Docker daemon not running${NC}"
    echo "Please start Docker daemon"
    exit 1
fi

echo -e "${GREEN}✓ Docker is installed and running${NC}"

# Check Python
echo ""
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION installed${NC}"

# Check for Anthropic API key
echo ""
echo "Checking for Anthropic API key..."
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${YELLOW}⚠ ANTHROPIC_API_KEY not set${NC}"
    echo ""
    read -p "Enter your Anthropic API key (or press Enter to skip): " api_key
    if [ -n "$api_key" ]; then
        export ANTHROPIC_API_KEY="$api_key"
        echo "export ANTHROPIC_API_KEY='$api_key'" >> ~/.bashrc
        echo -e "${GREEN}✓ API key set${NC}"
    else
        echo -e "${YELLOW}⚠ Skipping API key setup${NC}"
    fi
else
    echo -e "${GREEN}✓ API key found${NC}"
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -q anthropic docker pandas numpy

echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Build Docker image
echo ""
echo "Building Docker sandbox image (this may take a few minutes)..."
cd tools/analytics/sandbox

if docker build -t python-analysis-sandbox:latest . > /tmp/docker_build.log 2>&1; then
    echo -e "${GREEN}✓ Docker image built successfully${NC}"
else
    echo -e "${RED}✗ Docker build failed${NC}"
    echo "Check /tmp/docker_build.log for details"
    exit 1
fi

cd ../../..

# Create output directories
echo ""
echo "Creating output directories..."
mkdir -p outputs/analysis
mkdir -p outputs/visualizations
echo -e "${GREEN}✓ Directories created${NC}"

# Test installation
echo ""
echo "Testing installation..."
cat > /tmp/test_python_analysis.py << 'EOF'
import asyncio
import pandas as pd
import numpy as np
from agents.python_analysis_agent import PythonAnalysisAgent

async def test():
    try:
        # Create simple test data
        data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=10),
            'value': np.random.randn(10).cumsum()
        })

        print("Testing Python Analysis Agent...")
        agent = PythonAnalysisAgent()

        # Simple test (no actual execution, just initialization)
        print("✓ Agent initialized successfully")

        agent.cleanup()
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test())
    exit(0 if success else 1)
EOF

if python3 /tmp/test_python_analysis.py; then
    echo -e "${GREEN}✓ Installation test passed${NC}"
else
    echo -e "${RED}✗ Installation test failed${NC}"
    exit 1
fi

rm /tmp/test_python_analysis.py

# Summary
echo ""
echo "================================================================"
echo -e "${GREEN}Setup completed successfully!${NC}"
echo "================================================================"
echo ""
echo "Next steps:"
echo "  1. Review documentation:"
echo "     • docs/PYTHON_ANALYSIS_AGENT.md"
echo "     • docs/QUICKSTART_PYTHON_ANALYSIS.md"
echo ""
echo "  2. Run the demo:"
echo "     cd examples"
echo "     python python_analysis_demo.py"
echo ""
echo "  3. Try your own analysis:"
echo "     from agents.python_analysis_agent import PythonAnalysisAgent"
echo "     agent = PythonAnalysisAgent()"
echo "     result = await agent.analyze('your query', your_data)"
echo ""
echo "For support, see: https://github.com/your-repo/issues"
echo ""
