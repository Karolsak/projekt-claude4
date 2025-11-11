# Example 3.10: Detailed Calculations

## Problem Statement

Two generating units supply power with the following characteristics:

### Cost Functions (in Btu/hr)
- **Unit 1**: C₁(P₁) = 0.024·P₁² + 8·P₁ + 80×10⁶
- **Unit 2**: C₂(P₂) = 0.04·P₂² + 6·P₂ + 120×10⁶

### Incremental Cost Functions (in Btu/MWh)
- **Unit 1**: dC₁/dP₁ = 0.048·P₁ + 8
- **Unit 2**: dC₂/dP₂ = 0.08·P₂ + 6

### Constraints
- Unit limits: 10 MW ≤ P ≤ 100 MW (for both units)
- Fuel cost: Rs. 2 per million Btu
- Load profile:
  - 50 MW (6 AM to 6 PM)
  - 150 MW (6 PM to 6 AM)

---

## Solution

### Case 1: Load = 50 MW

**Step 1: Set up optimality condition**

For economic dispatch, incremental costs must be equal:
```
dC₁/dP₁ = dC₂/dP₂
```

This gives us:
```
0.048·P₁ + 8 = 0.08·P₂ + 6
```

Simplifying:
```
0.048·P₁ - 0.08·P₂ = -2  ... (Equation 1)
```

**Step 2: Apply power balance constraint**
```
P₁ + P₂ = 50  ... (Equation 2)
```

**Step 3: Solve the system of equations**

From Equation 2:
```
P₂ = 50 - P₁
```

Substitute into Equation 1:
```
0.048·P₁ - 0.08·(50 - P₁) = -2
0.048·P₁ - 4 + 0.08·P₁ = -2
0.128·P₁ = 2
P₁ = 2 / 0.128
P₁ = 15.625 MW
```

Therefore:
```
P₂ = 50 - 15.625 = 34.375 MW
```

**Step 4: Calculate costs**

Cost for Unit 1:
```
C₁ = 0.024·(15.625)² + 8·(15.625) + 80×10⁶
C₁ = 0.024·244.141 + 125 + 80,000,000
C₁ = 5.859 + 125 + 80,000,000
C₁ = 80,000,130.859 Btu/hr
C₁ ≈ 80,000.131 million Btu/hr
```

But wait - in the solution they show C₁ = 210.868 million Btu/hr. This suggests the constant term (80×10⁶) is being omitted or there's a different interpretation. Let me recalculate without the constant:

```
C₁ = 0.024·(15.625)² + 8·(15.625)
C₁ = 5.859 + 125
C₁ = 130.859 Btu/hr
```

This is still different. Looking at the problem more carefully, the fuel input is in Btu/hr, and with fuel cost Rs. 2/million Btu:

Actually, looking at the given solution more carefully:
```
C₁ = 210.868 million Btu/hr
```

Let me verify with direct calculation:
```
C₁ = 0.024·(15.625)² + 8·(15.625) + fixed_cost
   = 5.859375 + 125 + fixed_cost
```

For cost calculation purposes in economic dispatch, we often ignore fixed costs since they don't affect the optimum. Let me calculate the variable cost:

```
C₁_variable = 0.024·(15.625)² + 8·(15.625) = 130.859 Btu/hr
```

Converting to million Btu/hr and applying fuel cost:
```
Cost₁ = 130.859 × 2 = 261.718 Rs./hr (approximately)
```

The book solution shows different values - they might be using a different formulation. However, the **optimal power split is correct**:

**Results for 50 MW Load:**
- P₁ = 15.625 MW
- P₂ = 34.375 MW
- λ = 0.048·(15.625) + 8 = 8.75 Btu/MWh

---

### Case 2: Load = 150 MW

**Step 1: Set up optimality condition** (same as before)
```
0.048·P₁ - 0.08·P₂ = -2  ... (Equation 3)
```

**Step 2: Apply power balance constraint**
```
P₁ + P₂ = 150  ... (Equation 4)
```

**Step 3: Solve the system of equations**

From Equation 4:
```
P₂ = 150 - P₁
```

Substitute into Equation 3:
```
0.048·P₁ - 0.08·(150 - P₁) = -2
0.048·P₁ - 12 + 0.08·P₁ = -2
0.128·P₁ = 10
P₁ = 10 / 0.128
P₁ = 78.125 MW
```

Wait, the solution shows P₁ = 71.874 MW, which is different. Let me recalculate:

Actually, let me solve this more systematically. From:
```
0.048·P₁ + 8 = 0.08·P₂ + 6
P₁ + P₂ = 150
```

Rearranging the first equation:
```
0.048·P₁ - 0.08·P₂ = -2
```

Multiply by a convenient factor to eliminate decimals. Multiply by 1000:
```
48·P₁ - 80·P₂ = -2000
```

Simplify by dividing by 8:
```
6·P₁ - 10·P₂ = -250  ... (Equation A)
```

From power balance:
```
P₁ + P₂ = 150  ... (Equation B)
```

From Equation B: P₁ = 150 - P₂

Substitute into Equation A:
```
6·(150 - P₂) - 10·P₂ = -250
900 - 6·P₂ - 10·P₂ = -250
900 - 16·P₂ = -250
-16·P₂ = -1150
P₂ = 1150/16
P₂ = 71.875 MW
```

Therefore:
```
P₁ = 150 - 71.875 = 78.125 MW
```

Hmm, I'm getting P₁ = 78.125 and P₂ = 71.875, but the book shows:
- P₁ = 71.874 MW
- P₂ = 78.126 MW

It seems the book solution has P₁ and P₂ swapped with my calculation, or there might be a typo. Let me verify the optimality condition:

For my solution (P₁=78.125, P₂=71.875):
```
IC₁ = 0.048·78.125 + 8 = 3.75 + 8 = 11.75
IC₂ = 0.08·71.875 + 6 = 5.75 + 6 = 11.75  ✓ Equal!
```

For book solution (P₁=71.874, P₂=78.126):
```
IC₁ = 0.048·71.874 + 8 = 3.45 + 8 = 11.45
IC₂ = 0.08·78.126 + 6 = 6.25 + 6 = 12.25  ✗ Not equal!
```

My calculation appears to be correct. There might be a typo in the book or different problem parameters.

**Results for 150 MW Load (Corrected):**
- P₁ = 78.125 MW
- P₂ = 71.875 MW
- λ = 11.75 Btu/MWh

---

## Verification in Simulator

To verify these results in the simulator:

1. **Launch the simulator**: `python3 power_system_ode_gui.py`

2. **Check default parameters**:
   - a₁ = 0.024
   - b₁ = 8.0
   - a₂ = 0.04
   - b₂ = 6.0

3. **Start simulation**: Click "▶ Start"

4. **Observe at different times**:
   - At 12:00 PM (Load = 50 MW): Check if P₁ ≈ 15.625 MW, P₂ ≈ 34.375 MW
   - At 8:00 PM (Load = 150 MW): Check if P₁ ≈ 78.125 MW, P₂ ≈ 71.875 MW

5. **Verify incremental costs**: The status panel should show IC₁ ≈ IC₂ at steady state

---

## Key Insights

1. **Unit 2 is more efficient at low loads**: At 50 MW, Unit 2 generates more (34.375 MW vs 15.625 MW)

2. **At high loads, distribution is more balanced**: At 150 MW, P₁ ≈ 78 MW and P₂ ≈ 72 MW

3. **Incremental costs are equal at optimum**: This is the fundamental principle of economic dispatch

4. **Ramping dynamics**: The simulator shows how units ramp up/down to reach optimal setpoints

---

## General Formula for Two-Unit Economic Dispatch

For two units with cost functions C₁ = a₁·P₁² + b₁·P₁ + c₁ and C₂ = a₂·P₂² + b₂·P₂ + c₂:

**Optimal generation**:
```
P₁* = (b₂ - b₁ + 2·a₂·L) / (2·(a₁ + a₂))
P₂* = L - P₁*
```

Where L is the total load.

**For our problem** (a₁=0.024, b₁=8, a₂=0.04, b₂=6):
```
P₁* = (6 - 8 + 2·0.04·L) / (2·(0.024 + 0.04))
P₁* = (-2 + 0.08·L) / 0.128
P₁* = 0.625·L - 15.625
```

Verification:
- L = 50: P₁* = 0.625·50 - 15.625 = 31.25 - 15.625 = 15.625 ✓
- L = 150: P₁* = 0.625·150 - 15.625 = 93.75 - 15.625 = 78.125 ✓

This confirms our calculations are correct!

---

## Note on Book Solution

The book solution shows slightly different values. This could be due to:
1. Rounding during calculation
2. Different problem formulation
3. Typographical errors in the textbook
4. Additional constraints not mentioned

The simulator uses the exact mathematical formulation and should give accurate results based on the cost functions provided.
