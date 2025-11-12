# Quick Start Guide - Unit Commitment Simulator

## Installation

### 1. Install Required Packages

```bash
pip install -r requirements_uc.txt
```

On Linux, you may also need to install tkinter:
```bash
sudo apt-get install python3-tk
```

### 2. Verify Installation

Run the simple test (no GUI):
```bash
python3 test_uc_simple.py
```

You should see output matching Example 4.2 from the textbook, including:
- Unit cost calculations
- Optimal commitment for 8 MW load
- Economic dispatch results
- UC table

## Running the Application

### Launch GUI Simulator

```bash
python3 unit_commitment_simulator.py
```

## Quick Tutorial

### Step 1: View Static Results
- The UC table is automatically calculated on startup
- Scroll through the bottom-right panel to see the complete unit commitment table
- Use the "Current Load Demand" slider to see optimal commitment for different loads

### Step 2: Run Dynamic Simulation
1. Adjust "Dynamic Load Parameters":
   - **Base Load**: Set to 8 MW (default)
   - **Amplitude**: Set to 5 MW for visible variation
   - **Frequency**: Set to 0.5 Hz for moderate changes

2. Click **"Start Simulation"** button

3. Observe the real-time plots:
   - **Top Left**: Load varying sinusoidally over time
   - **Top Right**: Total cost adapting to load changes
   - **Bottom Left**: Individual unit outputs (colored lines)
   - **Bottom Right**: Cost vs load scatter plot

4. Status panel shows real-time:
   - Current time
   - Load demand
   - Generation cost
   - Lambda (incremental cost)
   - Power from each unit

### Step 3: Experiment with Parameters
- Adjust **Simulation Speed** (0.1-5.0x) to slow down or speed up
- Change **Time Step** for different integration accuracy
- Try different **ODE Methods**: Euler (simple) vs RK45 (accurate)
- Modify **Unit 1 Parameters** (a, b coefficients) and click "Recalculate UC Table"

### Step 4: Analyze Results
- Click **"Stop Simulation"** to pause
- Use **"Reset Data"** to clear plots and start fresh
- Resize the window - all elements adjust automatically

## Key Features to Explore

### 1. Load Patterns
Try different dynamic load scenarios:
- **Steady Load**: Set amplitude = 0, frequency = 0
- **Slow Variation**: amplitude = 3, frequency = 0.2
- **Fast Variation**: amplitude = 8, frequency = 1.5
- **High Load**: base = 20, amplitude = 5

### 2. Unit Commitment Changes
Watch how units turn on/off as load crosses thresholds:
- Below 5 MW: Only Unit 1
- 6-13 MW: Units 1 & 2
- 14-18 MW: Units 1, 2 & 3
- Above 19 MW: All 4 units

### 3. Economic Efficiency
Observe in the Cost vs Load plot:
- Linear regions: Single unit operating
- Jumps: Additional unit committed
- Slope changes: Different unit combinations

### 4. Parameter Sensitivity
Modify Unit 1 cost coefficients:
- Increase 'a': Steeper cost curve → higher costs at high loads
- Increase 'b': Higher fixed cost → more expensive overall
- After changes, click "Recalculate UC Table" to see new optimal strategy

## Understanding the Plots

### Plot 1: Load Demand vs Time
- **Blue line**: Current load demand
- Shows sinusoidal variation based on your parameters
- Range: 1-56 MW (system capacity)

### Plot 2: Total Cost vs Time
- **Red line**: Total generation cost
- Increases with load
- Jumps when new units commit
- Measured in Rs/hr (Rupees per hour)

### Plot 3: Unit Power Outputs vs Time
- **Blue**: Unit 1 (most economical, always on first)
- **Green**: Unit 2 (second choice)
- **Red**: Unit 3 (third choice)
- **Orange**: Unit 4 (least economical)
- Watch units turn on/off as load changes

### Plot 4: Cost vs Load Characteristic
- **Light blue dots**: Historical points
- **Red star**: Current operating point
- Shows system cost function
- Notice the piecewise structure

## Troubleshooting

### GUI doesn't start
**Error**: `ModuleNotFoundError: No module named 'tkinter'`

**Solution**:
- Ubuntu/Debian: `sudo apt-get install python3-tk`
- Fedora: `sudo dnf install python3-tkinter`
- macOS: tkinter included with Python
- Windows: tkinter included with Python

### Plots not updating
1. Check simulation speed isn't too fast
2. Increase time step
3. Stop and restart simulation

### High CPU usage
1. Reduce simulation speed
2. Increase time step (e.g., 0.2 instead of 0.1)
3. Use Euler method instead of RK45

## Example Scenarios

### Scenario 1: Verify Textbook Example
1. Set "Current Load Demand" to 8 MW
2. Check Status panel shows:
   - Cost: ~205.11 Rs/hr
   - Unit 1: ~6.73 MW
   - Unit 2: ~1.27 MW
   - Lambda: ~27.88 Rs/MWh
3. Matches Example 4.2 from textbook ✓

### Scenario 2: Peak Load
1. Set base load to 40 MW
2. Set amplitude to 10 MW
3. Start simulation
4. Observe all 4 units operating during peaks

### Scenario 3: Load Following
1. Set frequency to 0.3 Hz
2. Set amplitude to 10 MW
3. Start simulation
4. Watch units commit and decommit dynamically

## Next Steps

- Read the full [README_UC_Simulator.md](README_UC_Simulator.md) for detailed documentation
- Review [test_uc_simple.py](test_uc_simple.py) for calculation details
- Modify unit parameters to model your own generators
- Extend with additional units or constraints

## Keyboard Shortcuts

- Close window: Alt+F4 (Linux), Cmd+W (macOS), Alt+F4 (Windows)
- No other shortcuts implemented (use mouse for controls)

## Performance Tips

For smooth operation:
1. Keep time step ≥ 0.1s
2. Simulation speed ≤ 2.0x
3. Close other heavy applications
4. Use Euler for faster (less accurate) simulation
5. Use RK45 for accurate (slower) simulation

## Support

For issues or questions:
1. Check README_UC_Simulator.md for detailed information
2. Review the code comments in unit_commitment_simulator.py
3. Run test_uc_simple.py to verify calculations

Enjoy exploring Unit Commitment optimization!
