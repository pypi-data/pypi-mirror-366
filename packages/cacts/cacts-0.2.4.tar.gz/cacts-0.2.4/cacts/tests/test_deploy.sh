#!/bin/bash

# Shell-based deployment test for CACTS
# This script tests the installation and basic functionality of CACTS

set -e  # Exit on any error

echo "=== CACTS Deployment Test ==="

# Test 1: Check if CACTS can be imported
echo "Test 1: Checking if CACTS can be imported..."
python -c "import cacts; print('✓ CACTS import successful')"

# Test 2: Check if CACTS version is accessible
echo "Test 2: Checking CACTS version..."
python -c "import cacts; print(f'✓ CACTS version: {cacts.__version__}')"

# Test 3: Check if main entry point exists
echo "Test 3: Checking main entry point..."
python -c "from cacts import main; print('✓ Main entry point accessible')"

# Test 4: Check if CACTS can be run as a module (help output)
echo "Test 4: Testing CACTS as module (help)..."
if python -m cacts --help > /dev/null 2>&1; then
    echo "✓ CACTS can be run as module"
else
    echo "✗ CACTS module execution failed"
    exit 1
fi

# Test 5: Check if command line tools are available
echo "Test 5: Checking command line entry points..."
if python -c "from cacts import main, get_mach_env; print('✓ Entry points accessible')"; then
    echo "✓ Command line entry points work"
else
    echo "✗ Command line entry points failed"
    exit 1
fi

# Test 6: Test basic functionality with mock config
echo "Test 6: Testing with minimal mock configuration..."
# Create a temporary directory and mock config
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

cd "$TEMP_DIR"

# Initialize a git repo for testing
git init . > /dev/null 2>&1
git config user.email "test@example.com"
git config user.name "Test User"

# Create a minimal config file
cat > cacts.yaml << EOF
project:
  name: TestProject

machines:
  default:
    num_bld_res: 1
    num_run_res: 1
    env_setup: []
  
  local:
    num_bld_res: 1
    num_run_res: 1
    env_setup: []

configurations:
  default:
    longname: Default Test Build
    uses_baselines: False
    on_by_default: True
    cmake_args: {}
  
  test:
    longname: Test Build
    uses_baselines: False
    on_by_default: False
    cmake_args:
      CMAKE_BUILD_TYPE: Debug
EOF

# Create a minimal CMakeLists.txt
cat > CMakeLists.txt << EOF
cmake_minimum_required(VERSION 3.9)
project(TestProject)
EOF

# Test the config parsing (this should not fail)
echo "Testing config parsing..."
if python -c "
from cacts.parse_config import parse_project, parse_machine, parse_builds
import pathlib
config_file = pathlib.Path('cacts.yaml')
project = parse_project(config_file, '.')
machine = parse_machine(config_file, project, 'default')  # Use default instead of local
builds = parse_builds(config_file, project, machine, False, ['test'])
print('✓ Config parsing successful')
print(f'  Project: {project.name}')
print(f'  Machine: {machine.name}')
print(f'  Builds: {[b.name for b in builds]}')
"; then
    echo "✓ Configuration parsing works"
else
    echo "✗ Configuration parsing failed"
    exit 1
fi

echo ""
echo "=== All deployment tests passed! ==="
echo "CACTS is ready for use."