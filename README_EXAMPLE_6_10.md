# Example 6.10: Hydro-Thermal Scheduling Dynamic Simulator

## Overview

This application provides a comprehensive dynamic simulation tool for analyzing hydro-thermal power system scheduling based on **Example 6.10** from power systems textbooks.

### Problem Description

A thermal station and a hydro-station supply an area jointly:
- **Hydro station**: Operates 16 hours daily
- **Thermal station**: Operates 24 hours daily
- **Thermal incremental fuel cost**: CT = 6 + 12·PGT + 0.04·PGT² Rs./hr
- **Thermal load** (when both plants operate): 350 MW
- **Hydro incremental water rate**: dω/dPGH = 28 + 0.03·PGH m³/s
- **Total water available**: 450 million m³ for 16-hour operation

### Solution Results
- **Lambda (λ)**: 40.0000 Rs./MWh
- **Hydro Generation (PGH)**: 224.849 MW
- **Water Cost (γ)**: 1.15122 Rs./hr/m³/s

---

## Features

### 🎛️ Interactive Controls
- **9 Parameter Sliders**:
  - Thermal plant coefficients (a, b, c)
  - Hydro plant coefficients (α, β)
  - Total water available (million m³)
  - Hydro operating hours
  - Thermal load (MW)
  - Simulation time steps

### 🔬 ODE Solvers
- **RK45**: Runge-Kutta 4th/5th order adaptive method (high accuracy)
- **Euler**: Forward Euler method (educational comparison)

### 📊 Visualizations

#### Static Analysis (4 plots):
1. **Incremental Cost Curves**: Shows thermal and hydro incremental costs with optimal λ
2. **Generation Distribution**: Pie chart of power sharing
3. **Water Usage Profile**: Cumulative water consumption over time
4. **Cost Breakdown**: Bar chart comparing thermal, hydro, and total costs

#### Dynamic Simulation (6 plots):
1. **Power Generation vs Time**: Thermal, hydro, and total power over 16 hours
2. **Water Usage vs Time**: Cumulative water consumption with target line
3. **Lambda vs Time**: Incremental cost evolution
4. **Water Cost vs Time**: Real-time water cost (γ) changes
5. **Operating Costs vs Time**: Thermal, hydro, and total operating costs
6. **Cumulative Cost**: Total accumulated cost over simulation period

### 🔄 Dynamic Features
- **Automatic window resizing**: All plots adjust dynamically
- **Real-time parameter updates**: Sliders instantly affect calculations
- **Scrollable control panel**: Accommodates all controls comfortably
- **Comprehensive results display**: Detailed numerical results with verification

---

## Requirements

```bash
pip install numpy matplotlib scipy tkinter
```

**Note**: `tkinter` usually comes pre-installed with Python on most systems.

---

## Installation & Usage

### 1. Run the Application

```bash
python example_6_10_hydro_thermal_scheduling.py
```

### 2. Calculate Static Solution
Click **"Calculate Static Solution"** to solve the steady-state problem and view:
- Optimal power generation from each plant
- Water cost
- Economic analysis
- Static visualizations

### 3. Run Dynamic Simulation
1. Select ODE solver (RK45 recommended for accuracy)
2. Adjust parameters using sliders if desired
3. Click **"Run Dynamic Simulation"**
4. View real-time evolution of the system over 16 hours

### 4. Experiment with Parameters
Use sliders to explore different scenarios:
- **Increase water availability**: See how hydro generation increases
- **Change thermal coefficients**: Observe impact on optimal dispatch
- **Adjust hydro water rate**: Analyze water cost sensitivity
- **Modify operating hours**: Study time constraint effects

### 5. Reset to Defaults
Click **"Reset to Defaults"** to restore Example 6.10 original values.

---

## Technical Details

### Static Solution Method
Solves the optimization problem:
1. Calculate λ from thermal plant at given load: λ = dCT/dPGT
2. Solve quadratic equation for hydro power: β·PGH² + α·PGH - W_total/T = 0
3. Calculate water cost: γ = λ / (dω/dPGH)

### Dynamic Simulation Method
Models the system as an ODE problem:
- **State variables**: [PGH(t), water_used(t)]
- **Control law**: Proportional controller to track water usage
- **Dynamics**: Adjusts hydro power to maintain optimal dispatch while respecting water constraints

**ODE Solvers**:
- **RK45**: 4th-order accuracy with 5th-order error estimation (adaptive step size)
- **Euler**: 1st-order accuracy (fixed step size)

### Mathematical Formulation

**Thermal Cost Function**:
```
CT(PGT) = a + b·PGT + c·PGT²
dCT/dPGT = b + 2c·PGT = λ
```

**Hydro Water Rate**:
```
dω/dPGH = α + β·PGH
Water_used = ∫(α + β·PGH)·PGH dt
```

**Water Constraint**:
```
∫₀ᵀ (α + β·PGH(t))·PGH(t) dt = W_total
```

**Economic Dispatch**:
```
γ·(dω/dPGH) = λ (equal incremental cost principle)
```

---

## GUI Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                Hydro-Thermal Scheduling Simulator               │
├──────────────────┬──────────────────────────────────────────────┤
│  Control Panel   │           Visualization Area                 │
│  ┌────────────┐  │  ┌────────────┬────────────┐                │
│  │  Sliders   │  │  │  Plot 1    │  Plot 2    │                │
│  │  ────────  │  │  ├────────────┼────────────┤                │
│  │  thermal_a │  │  │  Plot 3    │  Plot 4    │                │
│  │  thermal_b │  │  ├────────────┼────────────┤                │
│  │     ...    │  │  │  Plot 5    │  Plot 6    │                │
│  │            │  │  └────────────┴────────────┘                │
│  ├────────────┤  │                                              │
│  │ ODE Solver │  │  (Auto-resizable matplotlib canvas)          │
│  │  ◉ RK45    │  │                                              │
│  │  ○ Euler   │  │                                              │
│  ├────────────┤  │                                              │
│  │  Buttons   │  │                                              │
│  ├────────────┤  │                                              │
│  │  Results   │  │                                              │
│  │  (Text)    │  │                                              │
│  └────────────┘  │                                              │
└──────────────────┴──────────────────────────────────────────────┘
```

---

## Example Scenarios

### Scenario 1: Increased Water Availability
```
Water: 450 → 600 million m³
Expected: Higher hydro generation, lower water cost
```

### Scenario 2: Reduced Operating Hours
```
Hydro Hours: 16 → 12 hours
Expected: Higher hydro power to use water within shorter time
```

### Scenario 3: Higher Thermal Costs
```
thermal_b: 12 → 20
Expected: Higher λ, potentially more hydro generation
```

---

## Troubleshooting

### Issue: Window doesn't resize properly
**Solution**: Maximize window or drag to desired size - plots auto-adjust

### Issue: Simulation fails with "No real solution"
**Solution**: Adjust parameters - ensure water availability matches operating hours

### Issue: Plots are too small
**Solution**: Increase window size - GUI uses responsive layout

### Issue: Solver takes too long
**Solution**:
- Reduce time_steps slider
- Use Euler for faster (but less accurate) results

---

## Educational Value

This simulator demonstrates:
1. **Economic Dispatch**: Equal incremental cost principle
2. **Hydro-Thermal Coordination**: Water constraint optimization
3. **Dynamic Optimization**: Real-time system evolution
4. **Numerical Methods**: Comparison of ODE solvers (RK45 vs Euler)
5. **Control Theory**: Feedback control for resource management
6. **Power Systems Economics**: Cost minimization with constraints

---

## Performance

- **Startup**: < 1 second
- **Static Calculation**: < 0.1 seconds
- **Dynamic Simulation (100 steps, RK45)**: < 2 seconds
- **Dynamic Simulation (100 steps, Euler)**: < 0.5 seconds
- **Memory Usage**: ~50-100 MB

---

## Future Enhancements

Potential additions:
- [ ] Multiple load scenarios (peak, off-peak)
- [ ] Multiple hydro plants
- [ ] Transmission losses
- [ ] Reservoir level dynamics
- [ ] Stochastic water inflow
- [ ] Optimization algorithms (PSO, GA)
- [ ] Export results to CSV/Excel
- [ ] 3D visualization of cost surfaces

---

## References

Based on **Example 6.10** from power systems textbooks covering:
- Economic dispatch
- Hydro-thermal coordination
- Water resource management
- Optimal power flow

---

## License

Educational use - Free to use and modify

---

## Author

Created for power systems engineering education and research.

**Version**: 1.0
**Last Updated**: 2025
**Python Version**: 3.7+
