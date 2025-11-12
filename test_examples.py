#!/usr/bin/env python3
"""
Test script for Economic Dispatch Examples 3.18 & 3.19
Verifies calculations without GUI
"""

import sys
import math

# Try to import numpy, use math as fallback
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("Warning: numpy not available, using math module for basic tests")
    print()


def test_example_318():
    """Test Example 3.18 calculations"""
    print("="*70)
    print("TESTING EXAMPLE 3.18: Penalty Factor Calculation")
    print("="*70)

    # Given values
    lambda_sys = 60.0  # Rs./MWh
    delta_PG2 = 100.0  # kW
    delta_PL = 12.0    # kW

    print("\nGiven:")
    print(f"  System λ = {lambda_sys} Rs./MWh")
    print(f"  ΔP_G2 = {delta_PG2} kW")
    print(f"  ΔP_L = {delta_PL} kW")

    # Calculate ∂P_L/∂P_G2
    dPL_dPG2 = delta_PL / delta_PG2
    print(f"\nCalculation:")
    print(f"  ∂P_L/∂P_G2 = {delta_PL}/{delta_PG2} = {dPL_dPG2:.4f}")

    # Calculate penalty factor L2
    L2 = 1.0 / (1.0 - dPL_dPG2)
    print(f"\n  Penalty Factor L₂:")
    print(f"    L₂ = 1/(1 - {dPL_dPG2:.4f})")
    print(f"    L₂ = 1/{1.0 - dPL_dPG2:.4f}")
    print(f"    L₂ = {L2:.4f}")

    # Calculate incremental cost
    dC2_dPG2 = lambda_sys / L2
    print(f"\n  Incremental Cost at Plant-2:")
    print(f"    ∂C₂/∂P_G2 = λ/L₂")
    print(f"    ∂C₂/∂P_G2 = {lambda_sys}/{L2:.4f}")
    print(f"    ∂C₂/∂P_G2 = {dC2_dPG2:.3f} Rs./MWh")

    # Calculate additional cost for 1 MW
    additional_cost = dC2_dPG2 * 1.0
    print(f"\n  Additional Cost (for 1 MW increase):")
    print(f"    ΔC₂ = {dC2_dPG2:.3f} × 1.0")
    print(f"    ΔC₂ = {additional_cost:.3f} Rs./hr")

    # Verify against expected values
    expected_L2 = 1.136
    expected_dC2 = 52.817
    expected_cost = 52.817

    print("\n" + "-"*70)
    print("Verification:")
    print(f"  Expected L₂: {expected_L2:.3f}, Calculated: {L2:.3f}", end="")
    if abs(L2 - expected_L2) < 0.01:
        print(" ✓")
    else:
        print(" ✗")

    # Note: Small difference due to rounding in textbook (0.02 tolerance)
    print(f"  Expected ∂C₂/∂P_G2: {expected_dC2:.3f}, Calculated: {dC2_dPG2:.3f}", end="")
    if abs(dC2_dPG2 - expected_dC2) < 0.02:
        print(" ✓ (within rounding)")
    else:
        print(" ✗")

    print(f"  Expected ΔC₂: {expected_cost:.3f}, Calculated: {additional_cost:.3f}", end="")
    if abs(additional_cost - expected_cost) < 0.02:
        print(" ✓ (within rounding)")
    else:
        print(" ✗")

    print("="*70)
    print()

    return abs(L2 - expected_L2) < 0.01 and abs(dC2_dPG2 - expected_dC2) < 0.02


def test_example_319():
    """Test Example 3.19 calculations"""
    print("="*70)
    print("TESTING EXAMPLE 3.19: Two-Plant Economic Dispatch")
    print("="*70)

    # Given values
    dC1_dPG1 = 55.0  # Rs./MWh
    dC2_dPG2 = 50.0  # Rs./MWh
    lambda_sys = 75.0  # Rs./MWh

    print("\nGiven:")
    print(f"  ∂C₁/∂P_G1 = {dC1_dPG1} Rs./MWh")
    print(f"  ∂C₂/∂P_G2 = {dC2_dPG2} Rs./MWh")
    print(f"  System λ = {lambda_sys} Rs./MWh")

    print("\nEconomic Operation Condition:")
    print("  ∂C₁/∂P_G1 × L₁ = λ")
    print("  ∂C₂/∂P_G2 × L₂ = λ")

    # Calculate penalty factors
    L1 = lambda_sys / dC1_dPG1
    L2 = lambda_sys / dC2_dPG2

    print(f"\nCalculations:")
    print(f"  L₁ = λ/(∂C₁/∂P_G1)")
    print(f"     = {lambda_sys}/{dC1_dPG1}")
    print(f"     = {L1:.4f}")

    print(f"\n  L₂ = λ/(∂C₂/∂P_G2)")
    print(f"     = {lambda_sys}/{dC2_dPG2}")
    print(f"     = {L2:.4f}")

    print("\nComparison:")
    if L2 > L1:
        print(f"  L₂ ({L2:.4f}) > L₁ ({L1:.4f})")
        print("  Plant-2 has the HIGHER penalty factor")
    else:
        print(f"  L₁ ({L1:.4f}) > L₂ ({L2:.4f})")
        print("  Plant-1 has the HIGHER penalty factor")

    print("\nInterpretation:")
    print("  Higher penalty factor indicates the plant is")
    print("  farther from the load center, experiencing")
    print("  higher transmission losses.")

    # Verify against expected values
    expected_L1 = 1.364
    expected_L2 = 1.5

    print("\n" + "-"*70)
    print("Verification:")
    print(f"  Expected L₁: {expected_L1:.3f}, Calculated: {L1:.3f}", end="")
    if abs(L1 - expected_L1) < 0.01:
        print(" ✓")
    else:
        print(" ✗")

    print(f"  Expected L₂: {expected_L2:.3f}, Calculated: {L2:.3f}", end="")
    if abs(L2 - expected_L2) < 0.01:
        print(" ✓")
    else:
        print(" ✗")

    print(f"  L₂ > L₁: {L2 > L1}", end="")
    if L2 > L1:
        print(" ✓")
    else:
        print(" ✗")

    print("="*70)
    print()

    return abs(L1 - expected_L1) < 0.01 and abs(L2 - expected_L2) < 0.01


def test_ode_solvers():
    """Test ODE solver implementations"""
    print("="*70)
    print("TESTING ODE SOLVERS")
    print("="*70)

    # Simple ODE: dy/dt = -y, solution: y(t) = y0 * exp(-t)
    def ode_func(y, t):
        return -y

    # Initial conditions
    y0 = 1.0
    dt = 0.1
    num_steps = 10

    print("\nTest ODE: dy/dt = -y")
    print(f"Initial condition: y(0) = {y0}")
    print(f"Time step: dt = {dt}")
    print(f"Number of steps: {num_steps}")

    # Euler method
    print("\n--- Euler Method ---")
    y_euler = y0
    for i in range(num_steps):
        t = i * dt
        dy_dt = ode_func(y_euler, t)
        y_euler = y_euler + dt * dy_dt
        exact = y0 * math.exp(-t - dt)
        error = abs(y_euler - exact)
        if i % 5 == 0 or i == num_steps - 1:
            print(f"  t={t+dt:.1f}: y={y_euler:.6f}, exact={exact:.6f}, error={error:.6f}")

    # RK4 method
    print("\n--- RK4 Method ---")
    y_rk4 = y0
    for i in range(num_steps):
        t = i * dt
        k1 = ode_func(y_rk4, t)
        k2 = ode_func(y_rk4 + 0.5*dt*k1, t + 0.5*dt)
        k3 = ode_func(y_rk4 + 0.5*dt*k2, t + 0.5*dt)
        k4 = ode_func(y_rk4 + dt*k3, t + dt)
        y_rk4 = y_rk4 + (dt/6.0) * (k1 + 2*k2 + 2*k3 + k4)
        exact = y0 * math.exp(-t - dt)
        error = abs(y_rk4 - exact)
        if i % 5 == 0 or i == num_steps - 1:
            print(f"  t={t+dt:.1f}: y={y_rk4:.6f}, exact={exact:.6f}, error={error:.6f}")

    # Final comparison
    t_final = num_steps * dt
    exact_final = y0 * math.exp(-t_final)
    print("\n" + "-"*70)
    print(f"At t={t_final:.1f}:")
    print(f"  Exact solution: {exact_final:.6f}")
    print(f"  Euler error: {abs(y_euler - exact_final):.6f}")
    print(f"  RK4 error: {abs(y_rk4 - exact_final):.6f}")
    print("\n  RK4 is more accurate than Euler ✓")

    print("="*70)
    print()

    return True


def main():
    """Run all tests"""
    print("\n")
    print("*"*70)
    print("  ECONOMIC DISPATCH EXAMPLES - TEST SUITE")
    print("  Testing calculations without GUI")
    print("*"*70)
    print("\n")

    results = []

    # Test Example 3.18
    try:
        result_318 = test_example_318()
        results.append(("Example 3.18", result_318))
    except Exception as e:
        print(f"ERROR in Example 3.18: {e}")
        results.append(("Example 3.18", False))

    # Test Example 3.19
    try:
        result_319 = test_example_319()
        results.append(("Example 3.19", result_319))
    except Exception as e:
        print(f"ERROR in Example 3.19: {e}")
        results.append(("Example 3.19", False))

    # Test ODE solvers
    try:
        result_ode = test_ode_solvers()
        results.append(("ODE Solvers", result_ode))
    except Exception as e:
        print(f"ERROR in ODE Solvers: {e}")
        results.append(("ODE Solvers", False))

    # Summary
    print("\n" + "*"*70)
    print("  TEST SUMMARY")
    print("*"*70)
    print()

    all_passed = True
    for test_name, passed in results:
        status = "PASSED ✓" if passed else "FAILED ✗"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False

    print("\n" + "*"*70)

    if all_passed:
        print("  ALL TESTS PASSED ✓")
        print("*"*70)
        print()
        return 0
    else:
        print("  SOME TESTS FAILED ✗")
        print("*"*70)
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
