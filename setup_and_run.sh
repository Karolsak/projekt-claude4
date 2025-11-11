#!/bin/bash

# Power System ODE Simulator - Setup and Run Script

echo "================================================"
echo "  Power System Economic Dispatch Simulator"
echo "  Setup and Installation"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

echo ""
echo "Installing required packages..."
pip3 install --user -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Warning: Some packages may not have installed correctly"
    echo "You may need to install them manually:"
    echo "  pip3 install numpy matplotlib"
fi

echo ""
echo "================================================"
echo "  Installation Complete!"
echo "================================================"
echo ""
echo "To run the simulator, execute:"
echo "  python3 power_system_ode_gui.py"
echo ""
echo "Or run this script again to launch automatically:"
echo "  ./setup_and_run.sh run"
echo ""

# If 'run' argument is provided, launch the application
if [ "$1" = "run" ]; then
    echo "Launching Power System Simulator..."
    python3 power_system_ode_gui.py
fi
