#!/bin/bash

echo "🎯 PET Resource Allocation Dashboard - Quick Start"
echo "============================================================"

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3."
    exit 1
fi

echo "✅ Found Python: $PYTHON_CMD"

# Install requirements if needed
if ! $PYTHON_CMD -c "import streamlit" 2>/dev/null; then
    echo "🔄 Installing Streamlit..."
    $PYTHON_CMD -m pip install streamlit pandas plotly numpy
fi

# Check for data files
if [ ! -d "data" ] || [ -z "$(ls -A data/*.csv 2>/dev/null)" ]; then
    echo "❌ No CSV files found in data/ directory"
    echo "💡 Please add your PET Resource Allocation CSV files to the data/ folder"
    exit 1
fi

echo "✅ Data files found"
echo ""
echo "🚀 Starting dashboard..."
echo "📊 Will open at: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop"
echo "============================================================"

# Start Streamlit
$PYTHON_CMD -m streamlit run app.py --server.headless false --browser.gatherUsageStats false
