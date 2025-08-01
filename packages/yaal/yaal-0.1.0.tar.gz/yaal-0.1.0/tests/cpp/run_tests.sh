#!/bin/bash

# YAAL C++ Tests Runner

set -e

echo "🔨 Building YAAL C++ Tests"
echo "=========================="

# Create build directory
mkdir -p build
cd build

# Configure with CMake
cmake ..

# Build the tests
make -j$(nproc)

echo ""
echo "🧪 Running YAAL C++ Tests"
echo "========================="

# Run the tests
./yaal_tests

echo ""
echo "✅ C++ tests completed!"