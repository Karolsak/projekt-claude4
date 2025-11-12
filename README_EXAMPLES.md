# Power System Economic Dispatch Simulator
## Examples 3.18 & 3.19: Penalty Factors and Economic Operation

A comprehensive Python application with tkinter GUI for simulating and visualizing power system economic dispatch problems with real-time ODE solvers.

## Features

### Core Capabilities
- **Real-time ODE Solvers**: Choose between RK45 (Runge-Kutta 4th order) and Euler methods
- **Dynamic Visualization**: Live updating graphs with matplotlib
- **Responsive Layout**: Automatic width and height adjustment when window resizes
- **Interactive Sliders**: Real-time parameter adjustment with immediate visual feedback
- **Tabbed Interface**: Separate tabs for Examples 3.18 and 3.19
- **Scrollable Controls**: Vertical scrollbars for control panels to fit any screen size

### Example 3.18: Penalty Factor Calculation

**Problem Statement:**
A power system operates an economic load dispatch with a system λ of 60 Rs./MWh. If raising the output of Plant-2 by 100 kW (while the other output is kept constant) results in increased power losses of 12 kW for the system, what is the approximate additional cost per hour if the output of this plant is increased by 1 MW?

**Features:**
- Interactive sliders for:
  - System λ (lambda): 30-100 Rs./MWh
  - ΔP_G2 (change in Plant-2 output): 10-500 kW
  - ΔP_L (change in losses): 1-100 kW

- Real-time calculations:
  - ∂P_L/∂P_G2 (loss sensitivity)
  - Penalty Factor L₂
  - Incremental cost ∂C₂/∂P_G2
  - Additional cost for 1 MW increase

- Dynamic graphs:
  1. Plant-2 Power Output vs Time
  2. System Losses vs Time
  3. Penalty Factor L₂ vs Time
  4. Incremental Cost vs Time

### Example 3.19: Two-Plant Economic Dispatch

**Problem Statement:**
A power system is supplied by only two plants, both of which operate on economical dispatch. At the bus of Plant-1, the incremental cost is 55 Rs./MWh and at Plant-2 is 50 Rs./MWh. Which plant has the higher penalty factor? What is the penalty factor of Plant-1 if the cost per hour of increasing the load on system by 1 MW is 75 Rs./hr?

**Features:**
- Interactive sliders for:
  - ∂C₁/∂P_G1: 30-100 Rs./MWh
  - ∂C₂/∂P_G2: 30-100 Rs./MWh
  - System λ: 40-120 Rs./MWh

- Real-time calculations:
  - Penalty Factor L₁ for Plant-1
  - Penalty Factor L₂ for Plant-2
  - Comparison and analysis
  - Economic dispatch allocation

- Dynamic graphs:
  1. Power Generation (both plants) vs Time
  2. Penalty Factors Comparison vs Time
  3. Total System Generation vs Time
  4. Current Power Distribution (Pie Chart)

## Installation

### Requirements
- Python 3.6 or higher
- tkinter (usually comes with Python, or install separately on Linux)
- numpy
- matplotlib
- scipy

### Install Dependencies

**On Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
pip3 install --user numpy matplotlib scipy
```

**On Fedora/RHEL:**
```bash
sudo dnf install python3-tkinter
pip3 install --user numpy matplotlib scipy
```

**On macOS:**
```bash
# tkinter comes with Python from python.org
pip3 install --user numpy matplotlib scipy
```

**On Windows:**
```bash
# tkinter comes with Python installer
pip install numpy matplotlib scipy
```

## Usage

### Quick Start

**Option 1: Using the launcher (recommended)**
```bash
python3 run_examples.py
```

The launcher will:
- Check all dependencies
- Provide helpful installation instructions if needed
- Launch the application if everything is ready

**Option 2: Direct execution**
```bash
python3 economic_dispatch_examples.py
```

### Using the Application

1. **Select Example Tab**: Click on "Example 3.18" or "Example 3.19" tab

2. **Adjust Parameters**: Use the sliders to change system parameters
   - Changes are reflected immediately in calculations and graphs

3. **Choose ODE Solver**: Select between RK45 (more accurate) or Euler (faster)

4. **Run Simulation**:
   - Click "▶ Start" to begin dynamic simulation
   - Click "⏸ Pause" to pause
   - Click "↻ Reset" to reset to initial conditions

5. **Observe Results**:
   - Results panel shows detailed calculations
   - Graphs update in real-time
   - Watch how parameters affect the system dynamically

### Window Controls

- **Resize Window**: Drag window edges - all elements resize automatically
- **Scroll Controls**: Use mouse wheel or scrollbar to navigate control panel
- **Tab Switching**: Click between Example tabs to switch problems

## Mathematical Background

### Example 3.18 Calculations

Given:
- System λ (lambda): System incremental cost
- ΔP_G2: Change in Plant-2 output
- ΔP_L: Change in system losses

Calculations:
```
∂P_L/∂P_G2 = ΔP_L / ΔP_G2

Penalty Factor:
L₂ = 1 / (1 - ∂P_L/∂P_G2)

Incremental Cost at Plant-2:
∂C₂/∂P_G2 = λ / L₂

Additional Cost (for 1 MW):
ΔC₂ = (∂C₂/∂P_G2) × 1.0 MW
```

### Example 3.19 Calculations

For economic operation:
```
∂C₁/∂P_G1 × L₁ = λ
∂C₂/∂P_G2 × L₂ = λ
```

Therefore:
```
L₁ = λ / (∂C₁/∂P_G1)
L₂ = λ / (∂C₂/∂P_G2)
```

The plant with the higher penalty factor is farther from the load center (higher transmission losses).

## ODE Solver Methods

### RK45 (Runge-Kutta 4th Order)
- More accurate
- Uses 4 intermediate steps per time step
- Better for stiff systems
- Recommended for precise simulations

### Euler Method
- Simpler, faster
- First-order accuracy
- Good for quick approximations
- Educational purposes

## Dynamic Simulation

The application simulates power system dynamics using ODEs:
```python
dP/dt = (P_target - P_current) / τ
```

Where:
- P: Power generation
- P_target: Optimal economic dispatch setpoint
- τ: Time constant (system response speed)

This models how real generators ramp up/down to meet load changes while maintaining economic operation.

## File Structure

```
.
├── economic_dispatch_examples.py    # Main application
├── run_examples.py                  # Launcher script
├── README_EXAMPLES.md               # This file
├── power_system_ode_gui.py         # Original Example 3.10
└── run_simulator.py                 # Launcher for Example 3.10
```

## Troubleshooting

### "No module named 'tkinter'"
- On Linux: `sudo apt-get install python3-tk` or `sudo dnf install python3-tkinter`
- On macOS/Windows: Reinstall Python from official source

### "No module named 'numpy'" (or matplotlib, scipy)
```bash
pip3 install --user numpy matplotlib scipy
```

### Graphics not displaying
- Ensure you're running in a graphical environment (not headless)
- Check that matplotlib backend supports your system
- Try: `export MPLBACKEND=TkAgg` before running

### Slow performance
- Switch from RK45 to Euler method
- Close other applications
- Reduce window size

## Educational Use

This simulator is designed for:
- Power systems engineering courses
- Economic dispatch education
- ODE solver method comparison
- Real-time control system visualization
- Understanding penalty factors and transmission losses

## Technical Details

- **Language**: Python 3
- **GUI Framework**: tkinter
- **Plotting**: matplotlib with FigureCanvasTkAgg
- **ODE Integration**: Custom RK4 and Euler implementations
- **Grid Layout**: Responsive with weight-based resizing
- **Update Rate**: 50ms (20 Hz)

## License

Educational and research use.

## Support

For issues or questions:
1. Check that all dependencies are installed
2. Verify Python version (3.6+)
3. Review error messages carefully
4. Check README troubleshooting section

## Version

Version 1.0 - November 2025

---

**Note**: This application requires a graphical environment (X server on Linux, display on macOS/Windows). It will not run in headless environments without X forwarding or VNC.
