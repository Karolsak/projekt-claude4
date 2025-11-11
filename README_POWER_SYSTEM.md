# Power System Economic Dispatch Simulator

A dynamic simulation tool for power system economic dispatch with real-time ODE solvers, built with Python and tkinter.

## Features

### 🚀 Core Functionality
- **Real-time ODE Solver**: Choose between RK45 (Runge-Kutta 4th order) and Euler methods
- **Dynamic Simulation**: Simulate power generation over 24-hour cycle
- **Economic Dispatch**: Optimal power allocation based on incremental cost equality
- **Interactive Visualization**: Four dynamic plots showing key system parameters

### 📊 Visualization
1. **Power Generation Plot**: Real-time tracking of Unit 1, Unit 2, and Load demand
2. **Total Cost Plot**: Generation cost over time in Rs./hr
3. **Incremental Cost (λ) Plot**: System lambda showing optimal dispatch point
4. **Power Distribution Pie Chart**: Current snapshot of generation distribution

### 🎛️ Interactive Controls
- **ODE Solver Selection**: Toggle between RK45 and Euler methods
- **Time Scale**: Adjust simulation speed (0.1x to 10x)
- **Unit 1 Parameters**:
  - Cost coefficient a₁ (quadratic term)
  - Cost coefficient b₁ (linear term)
  - Ramping rate (MW/s)
- **Unit 2 Parameters**:
  - Cost coefficient a₂ (quadratic term)
  - Cost coefficient b₂ (linear term)
  - Ramping rate (MW/s)

### 🔄 Automatic Window Resizing
- Fully responsive layout
- Plots automatically adjust to window size
- Grid-based layout for optimal space utilization

## Problem Description (Example 3.10)

### Given Data
**Unit 1 Cost Function:**
```
C₁(P₁) = 0.024·P₁² + 8·P₁ + 80×10⁶ Btu/hr
```

**Unit 2 Cost Function:**
```
C₂(P₂) = 0.04·P₂² + 6·P₂ + 120×10⁶ Btu/hr
```

**Unit Limits:**
- Minimum: 10 MW
- Maximum: 100 MW

**Load Profile:**
- 50 MW (6 AM to 6 PM)
- 150 MW (6 PM to 6 AM)

**Fuel Cost:** Rs. 2 per million Btu

### Economic Dispatch Principle

For optimal economic dispatch, the incremental costs of all units must be equal:

```
dC₁/dP₁ = dC₂/dP₂ = λ (system lambda)
```

Where:
- `dC₁/dP₁ = 0.048·P₁ + 8`
- `dC₂/dP₂ = 0.08·P₂ + 6`

Subject to constraint: `P₁ + P₂ = Load`

### Solution for Example 3.10

**When Load = 50 MW:**
```
P₁ = 15.625 MW
P₂ = 34.375 MW
C₁ = 210.868 million Btu/hr
C₂ = 373.5 million Btu/hr
```

**When Load = 150 MW:**
```
P₁ = 71.874 MW
P₂ = 78.126 MW
C₁ = 851.496 million Btu/hr
C₂ = 757.87 million Btu/hr
```

**Total Daily Cost:** Rs. 52,649.61/hr (combined for both load periods)

## Installation

### Prerequisites
```bash
# Python 3.7 or higher
python3 --version

# Required packages
pip install numpy matplotlib
```

### Required Python Packages
- `tkinter` (usually included with Python)
- `numpy` - Numerical computations
- `matplotlib` - Plotting and visualization

## Usage

### Running the Application
```bash
python3 power_system_ode_gui.py
```

### Basic Operation

1. **Start Simulation**
   - Click the "▶ Start" button to begin simulation
   - The system will start from t=0 (midnight)

2. **Adjust Parameters**
   - Use sliders to modify cost coefficients
   - Change ramping rates to see dynamic response
   - Adjust time scale for faster/slower simulation

3. **Observe Results**
   - Watch real-time plots update
   - Monitor status panel for current values
   - See economic dispatch in action

4. **Pause/Reset**
   - Click "⏸ Pause" to temporarily stop
   - Click "↻ Reset" to restart from beginning

### Understanding the Interface

#### Control Panel (Left Side)
- **Simulation Controls**: Start, Pause, Reset buttons
- **ODE Solver Method**: Select integration method
- **Time Scale**: Control simulation speed
- **Unit Parameters**: Adjust cost functions and ramping
- **Status Display**: Real-time system information

#### Visualization Panel (Right Side)
- **Top Left**: Power generation time series
- **Top Right**: Total generation cost over time
- **Bottom Left**: System lambda (incremental cost)
- **Bottom Right**: Current power distribution pie chart

## Technical Details

### ODE System

The simulator models power generation dynamics as a first-order system:

```
dP₁/dt = (P₁_target - P₁) / τ₁
dP₂/dt = (P₂_target - P₂) / τ₂
```

Where:
- `P₁_target`, `P₂_target` are optimal setpoints from economic dispatch
- `τ₁`, `τ₂` are time constants (related to ramping rates)
- Ramping rate limits are enforced

### Numerical Methods

**RK45 (Runge-Kutta 4th Order):**
- Higher accuracy
- 4 function evaluations per step
- Recommended for precise simulation

**Euler Method:**
- Simpler, faster
- 1 function evaluation per step
- Good for quick exploration

### Economic Dispatch Algorithm

1. Calculate optimal generation using equal incremental cost:
   ```python
   P₁_optimal = (b₂ - b₁ + 2·a₂·Load) / (2·(a₁ + a₂))
   P₂_optimal = Load - P₁_optimal
   ```

2. Apply unit limits (10-100 MW)

3. Adjust for constraint violations

4. Calculate system lambda: `λ = dC₁/dP₁`

## Example Scenarios

### Scenario 1: Default Parameters (Example 3.10)
- Load changes from 50 MW to 150 MW at 6 PM
- System optimally redistributes generation
- Observe smooth transitions due to ramping constraints

### Scenario 2: Different Cost Coefficients
- Increase `a₁` to make Unit 1 more expensive
- Observe Unit 2 taking more load
- Lambda increases accordingly

### Scenario 3: Ramping Rate Effects
- Decrease ramping rates (slower units)
- Observe delayed response to load changes
- Study system dynamics

### Scenario 4: Method Comparison
- Run with RK45 and note smooth curves
- Switch to Euler and compare (may show slight differences at high speeds)

## Mathematical Background

### Cost Function (Quadratic)
```
C(P) = a·P² + b·P + c
```
- `a`: Quadratic coefficient (fuel efficiency factor)
- `b`: Linear coefficient (base efficiency)
- `c`: Fixed cost

### Incremental Cost
```
IC(P) = dC/dP = 2·a·P + b
```

### Optimality Condition
For economic dispatch without losses:
```
IC₁(P₁) = IC₂(P₂) = ... = ICₙ(Pₙ) = λ
```

Subject to:
```
Σ Pᵢ = Load
Pᵢ_min ≤ Pᵢ ≤ Pᵢ_max
```

## Troubleshooting

### Issue: Plots not updating
- **Solution**: Ensure matplotlib is properly installed
- Try: `pip install --upgrade matplotlib`

### Issue: Window too small
- **Solution**: Manually resize window - layout is fully responsive
- Default size: 1400x900 pixels

### Issue: Simulation running too fast/slow
- **Solution**: Adjust "Time Scale" slider
- Lower values = slower simulation
- Higher values = faster simulation

### Issue: Values seem incorrect
- **Solution**: Click "↻ Reset" to restart with default parameters
- Verify cost coefficients match expected values

## Advanced Features

### Custom Load Profiles
To modify the load profile, edit the `get_load_at_time()` method in the `PowerSystemSimulator` class:

```python
def get_load_at_time(self, t_hours):
    """Custom load profile"""
    t_mod = t_hours % 24
    # Add your custom logic here
    return load_value
```

### Adding More Units
The code can be extended to support additional generating units by:
1. Adding new state variables
2. Extending the ODE system
3. Modifying economic dispatch algorithm
4. Adding UI controls

### Exporting Data
To export simulation data, you can access:
- `simulator.time_history`
- `simulator.P1_history`
- `simulator.P2_history`
- `simulator.cost_history`
- `simulator.lambda_history`

## References

- Power System Operation and Control (Example 3.10)
- Optimal Power Flow and Economic Dispatch
- Numerical Methods for ODEs (RK45, Euler)

## License

This is an educational tool for understanding power system economics and ODE simulation.

## Author

Created for power systems engineering education and research.

---

**Note**: This simulator is for educational purposes. Real power systems involve additional complexities such as transmission losses, voltage constraints, reactive power, and security constraints.
