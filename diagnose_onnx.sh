#!/bin/bash
# Diagnostic script to identify onnxruntime installation issues
# Run inside Docker container: docker exec -it <container> bash /app/diagnose_onnx.sh

echo "========================================="
echo "ONNXRUNTIME DIAGNOSTIC REPORT"
echo "========================================="
echo ""

echo "1. SYSTEM INFORMATION"
echo "---------------------"
echo "Architecture: $(uname -m)"
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME)"
echo "Python version: $(python --version)"
echo ""

echo "2. INSTALLED PACKAGES"
echo "---------------------"
echo "Looking for onnxruntime..."
pip list | grep -i onnx || echo "❌ onnxruntime NOT found in pip list"
echo ""

echo "3. SYSTEM LIBRARIES"
echo "-------------------"
echo "libgomp1:"
dpkg -l | grep libgomp || echo "❌ libgomp1 NOT installed"
echo "libstdc++6:"
dpkg -l | grep libstdc++ || echo "❌ libstdc++6 NOT installed"
echo ""

echo "4. PYTHON IMPORT TEST"
echo "---------------------"
python -c "import onnxruntime; print('✅ onnxruntime import SUCCESS'); print('Version:', onnxruntime.__version__)" 2>&1 || echo "❌ onnxruntime import FAILED"
echo ""

echo "5. NUMPY TEST"
echo "-------------"
python -c "import numpy; print('✅ numpy import SUCCESS'); print('Version:', numpy.__version__)" 2>&1 || echo "❌ numpy import FAILED"
echo ""

echo "6. VAD MODEL FILE"
echo "-----------------"
ls -lh /app/models/silero_vad.onnx 2>&1 || echo "❌ silero_vad.onnx NOT found"
echo ""

echo "7. DETAILED IMPORT ERROR"
echo "------------------------"
python -c "import onnxruntime" 2>&1
echo ""

echo "8. PIP SHOW onnxruntime"
echo "-----------------------"
pip show onnxruntime 2>&1 || echo "❌ onnxruntime package not found"
echo ""

echo "========================================="
echo "DIAGNOSTIC COMPLETE"
echo "========================================="
