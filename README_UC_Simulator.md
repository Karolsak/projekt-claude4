# Unit Commitment Dynamic Simulator - Example 4.2

## Overview
A comprehensive Python application with Tkinter GUI for solving the Unit Commitment (UC) problem from Example 4.2. This simulator provides dynamic simulation capabilities with real-time ODE solvers, interactive controls, and visualization.

## Features

### Core Functionality
- **Unit Commitment Optimization**: Dynamic programming algorithm to find optimal unit commitment
- **Economic Dispatch**: Lambda iteration method for optimal load sharing among committed units
- **Dynamic Simulation**: Real-time simulation with varying load demands
- **ODE Solvers**: Multiple integration methods (Euler, RK45, RK23, DOP853)

### Interactive GUI Components
1. **Responsive Design**: Automatic width and height adjustment when window resizes
2. **Control Sliders**:
   - Current load demand (1-56 MW)
   - Base load for dynamic simulation
   - Load amplitude for sinusoidal variation
   - Frequency of load variation
   - Simulation speed control
   - Time step adjustment
   - Unit parameter adjustment (coefficients a, b)

3. **Real-time Visualization**:
   - Load demand vs time
   - Total generation cost vs time
   - Individual unit power outputs vs time
   - Cost vs load characteristic curve

4. **UC Table Display**:
   - Detailed unit commitment for each load level
   - Power allocation for each unit
   - Total generation cost
   - Summary status table

### Problem Specifications (Example 4.2)
- **4 Generating Units** with parameters from Table 4.5:
  - Unit 1: a=0.74, b=22.9, d=0, Capacity: 1-14 MW
  - Unit 2: a=1.56, b=25.9, d=0, Capacity: 1-14 MW
  - Unit 3: a=1.97, b=29.0, d=0, Capacity: 1-14 MW
  - Unit 4: a=1.36, b=31.2, d=0, Capacity: 1-14 MW

- **Cost Function**: F_i = 0.5 × a_i × P_i² + b_i × P_i + d_i
- **Incremental Cost**: dC/dP_i = a_i × P_i + b_i

## Installation

### Requirements
```bash
pip install -r requirements_uc.txt
```

### Required Packages
- Python 3.7+
- tkinter (usually comes with Python)
- numpy
- matplotlib
- scipy

## Usage

### Running the Application
```bash
python unit_commitment_simulator.py
```

### GUI Controls

#### Load Control
- **Current Load Demand Slider**: Adjust the instantaneous load (1-56 MW)
- View optimal unit commitment for the selected load

#### Dynamic Load Parameters
- **Base Load**: Average load level around which variation occurs
- **Amplitude**: Magnitude of load variation (0-10 MW)
- **Frequency**: Rate of load change (0.1-2.0 Hz)

#### Simulation Parameters
- **Speed**: Simulation playback speed (0.1-5.0x)
- **Time Step**: Integration time step (0.01-0.5 s)
- **ODE Method**: Select integration method
  - Euler: Simple first-order method
  - RK45: Runge-Kutta 4(5) adaptive method
  - RK23: Runge-Kutta 2(3) adaptive method
  - DOP853: High-order explicit method

#### Unit Parameters
- Adjust Unit 1 cost coefficients (a, b) dynamically
- System automatically recalculates UC table

#### Buttons
- **Start Simulation**: Begin dynamic simulation with load variations
- **Stop Simulation**: Pause the simulation
- **Reset Data**: Clear all historical data and plots
- **Recalculate UC Table**: Recompute optimal commitments

### Interpreting Results

#### Status Display
Shows real-time information:
- Current simulation time
- Load demand (MW)
- Total generation cost (Rs/hr)
- Lambda (incremental cost, Rs/MWh)
- Individual unit power outputs

#### Plot 1: Load Demand vs Time
- Blue line showing dynamic load variation
- Follows sinusoidal pattern based on base, amplitude, and frequency

#### Plot 2: Total Cost vs Time
- Red line showing generation cost
- Cost varies with load and unit commitment

#### Plot 3: Unit Power Outputs
- Four colored lines representing each unit
- Shows which units are committed and their power levels
- Units turn on/off based on optimal commitment strategy

#### Plot 4: Cost vs Load Characteristic
- Scatter plot showing cost-load relationship
- Red star indicates current operating point
- Shows system efficiency across load range

#### UC Table
Detailed table showing:
- Load range (MW)
- Minimum generation cost (Rs/hr)
- Power allocation to each unit
- Total power generated

Summary status table indicates unit on/off states for load ranges:
- 1-5 MW: Unit 1 only
- 6-13 MW: Units 1 & 2
- 14-18 MW: Units 1, 2 & 3
- 19-56 MW: All four units

## Algorithm Details

### Dynamic Programming Approach
The unit commitment problem is solved using dynamic programming:

1. **State Definition**: F[n][load] = minimum cost to supply 'load' using first 'n' units

2. **Recurrence Relation**:
   ```
   F[n][load] = min(F[n-1][load-p] + f_n(p))
   ```
   where p ranges over valid power outputs for unit n

3. **Complexity**: O(n × L × P) where:
   - n = number of units
   - L = maximum load
   - P = power range per unit

### Economic Dispatch
Lambda iteration method for optimal load sharing:

1. Start with lambda bounds [λ_min, λ_max]
2. For middle lambda, calculate power: P_i = (λ - b_i) / a_i
3. Constrain to unit limits: P_min ≤ P_i ≤ P_max
4. If total power matches load (within tolerance), stop
5. Otherwise, adjust lambda bounds and repeat

### Dynamic Simulation
The system dynamics are modeled as:

```
dP_i/dt = (P_target_i - P_i) / τ
```

Where:
- P_i = current power output of unit i
- P_target_i = optimal power from economic dispatch
- τ = time constant (response time)

Load varies as:
```
Load(t) = Base + Amplitude × sin(2π × Frequency × t)
```

## Example Solutions

### For 8 MW Load Demand
From the textbook example:
- **Optimal Commitment**: Unit 1 (7 MW) + Unit 2 (1 MW)
- **Total Cost**: 205.11 Rs/hr
- **Lambda**: 27.88 Rs/MWh

### Detailed Calculations (from Example 4.2)
Unit 1 supplies 6.73 MW: f₁(6.73) = 170.87 Rs/hr
Unit 2 supplies 1.27 MW: f₂(1.27) = 34.15 Rs/hr
Total cost: 205.02 Rs/hr (slight difference due to rounding)

## Key Insights

1. **Unit 1 is most economical** due to lowest cost coefficients
2. **Sequential commitment**: Units added in order of cost efficiency
3. **Load range determines commitment**:
   - Low loads: Single unit sufficient
   - High loads: Multiple units needed
4. **Economic dispatch ensures**: Equal incremental costs across all committed units

## Troubleshooting

### tkinter not found
If you get "ModuleNotFoundError: No module named 'tkinter'":
- **Linux**: `sudo apt-get install python3-tk`
- **macOS**: tkinter comes with Python
- **Windows**: tkinter comes with Python

### Plots not updating
- Ensure matplotlib backend supports GUI: `matplotlib.use('TkAgg')`
- Check that simulation speed is not too fast

### High CPU usage
- Reduce simulation speed
- Increase time step
- Reduce number of data points (max_time_points)

## Extensions and Modifications

### Adding More Units
Modify the `self.units` list in `__init__`:
```python
self.units.append({
    'name': 'Unit 5',
    'a': 1.2,
    'b': 28.0,
    'd': 0,
    'min': 1.0,
    'max': 20.0
})
```

### Changing Cost Function
Modify `cost_function` and `incremental_cost` methods for different formulations.

### Alternative Load Patterns
Modify `dynamic_load_function` for:
- Step changes
- Ramp variations
- Random load fluctuations
- Historical load profiles

## References
- Power System Operation and Control, Example 4.2
- Unit Commitment optimization using Dynamic Programming
- Economic Dispatch using Lambda Iteration

## Author
Generated for Power System Unit Commitment Analysis

## License
Educational and research purposes
