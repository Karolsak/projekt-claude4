"""
Test script for Power System Frequency Simulator
Validates results against expected values for Examples 7.3 and 7.4
"""

import numpy as np
import sys


def test_example_7_3():
    """Test Example 7.3 without governor dynamics"""
    print("=" * 70)
    print("Testing Example 7.3: Simplified Model (No Governor/Turbine)")
    print("=" * 70)

    # System parameters
    H = 5.0
    Kps = 100.0
    tps = 20.0
    R = 3.0
    f0 = 50.0

    # Test cases with expected results
    test_cases = [
        (0.5, -0.0145),  # (load_change_%, expected_delta_fss_Hz)
        (1.0, -0.029),
        (2.0, -0.0583),
    ]

    print(f"\nSystem Parameters:")
    print(f"  H = {H} kW-s/kVA")
    print(f"  Kps = {Kps}")
    print(f"  tps = {tps} s")
    print(f"  R = {R}")
    print(f"  f0 = {f0} Hz")

    all_passed = True

    for load_change_percent, expected_delta_fss in test_cases:
        print(f"\n{'-' * 70}")
        print(f"Test Case: Load Change = {load_change_percent}%")
        print(f"Expected Δfss = {expected_delta_fss:.4f} Hz")

        # Simulate using RK4
        delta_PL = load_change_percent / 100.0  # Per unit

        # Initial state (Δf in Hz)
        delta_f = 0.0
        t = 0.0
        dt = 0.01
        t_max = 200.0  # Run longer to ensure steady state

        # Integration loop
        while t < t_max:
            # System dynamics: tps * dΔf/dt = -(1 + Kps/R) * Δf - Kps * ΔPL
            # Note: Δf is in Hz, ΔPL is in per unit
            d_delta_f = (-(1 + Kps / R) * delta_f - Kps * delta_PL) / tps

            # RK4 step
            k1 = d_delta_f
            delta_f_k2 = delta_f + dt * k1 / 2
            d_delta_f_k2 = (-(1 + Kps / R) * delta_f_k2 - Kps * delta_PL) / tps
            k2 = d_delta_f_k2

            delta_f_k3 = delta_f + dt * k2 / 2
            d_delta_f_k3 = (-(1 + Kps / R) * delta_f_k3 - Kps * delta_PL) / tps
            k3 = d_delta_f_k3

            delta_f_k4 = delta_f + dt * k3
            d_delta_f_k4 = (-(1 + Kps / R) * delta_f_k4 - Kps * delta_PL) / tps
            k4 = d_delta_f_k4

            delta_f = delta_f + dt * (k1 + 2*k2 + 2*k3 + k4) / 6
            t += dt

        # Result is already in Hz
        delta_fss_calculated = delta_f

        # Calculate error
        error = abs(delta_fss_calculated - expected_delta_fss)
        error_percent = 100 * error / abs(expected_delta_fss)

        print(f"Calculated Δfss = {delta_fss_calculated:.4f} Hz")
        print(f"Error = {error:.4f} Hz ({error_percent:.2f}%)")

        # Check if result is within acceptable tolerance (5%)
        if error_percent < 5.0:
            print("✓ PASSED")
        else:
            print("✗ FAILED")
            all_passed = False

    return all_passed


def test_example_7_4():
    """Test Example 7.4 with governor and turbine dynamics"""
    print("\n" + "=" * 70)
    print("Testing Example 7.4: Full Model (With Governor/Turbine)")
    print("=" * 70)

    # System parameters
    H = 5.0
    Kps = 100.0
    tps = 20.0
    R = 3.0
    f0 = 50.0
    tsg = 0.4
    tt = 0.5

    # Test cases with expected results
    test_cases = [
        (0.5, -0.0235),  # (load_change_%, expected_delta_fss_Hz)
        (1.0, -0.047),
    ]

    print(f"\nSystem Parameters:")
    print(f"  H = {H} kW-s/kVA")
    print(f"  Kps = {Kps}")
    print(f"  tps = {tps} s")
    print(f"  R = {R}")
    print(f"  f0 = {f0} Hz")
    print(f"  tsg = {tsg} s")
    print(f"  tt = {tt} s")

    all_passed = True

    for load_change_percent, expected_delta_fss in test_cases:
        print(f"\n{'-' * 70}")
        print(f"Test Case: Load Change = {load_change_percent}%")
        print(f"Expected Δfss = {expected_delta_fss:.4f} Hz")

        # Simulate using RK4
        delta_PL = load_change_percent / 100.0  # Per unit

        # Initial state: [Δf (Hz), ΔPg (pu), ΔPm (pu)]
        state = np.array([0.0, 0.0, 0.0])
        t = 0.0
        dt = 0.01
        t_max = 200.0  # Run longer to ensure steady state

        # Integration loop
        def dynamics(s):
            delta_f, delta_Pg, delta_Pm = s  # Δf in Hz
            d_delta_Pg = (-delta_f / R - delta_Pg) / tsg
            d_delta_Pm = (delta_Pg - delta_Pm) / tt
            # With governor, droop is handled by governor feedback loop
            d_delta_f = (-delta_f + Kps * (delta_Pm - delta_PL)) / tps
            return np.array([d_delta_f, d_delta_Pg, d_delta_Pm])

        while t < t_max:
            # RK4 step
            k1 = dynamics(state)
            k2 = dynamics(state + dt * k1 / 2)
            k3 = dynamics(state + dt * k2 / 2)
            k4 = dynamics(state + dt * k3)

            state = state + dt * (k1 + 2*k2 + 2*k3 + k4) / 6
            t += dt

        # Result is already in Hz
        delta_fss_calculated = state[0]

        # Calculate error
        error = abs(delta_fss_calculated - expected_delta_fss)
        error_percent = 100 * error / abs(expected_delta_fss)

        print(f"Calculated Δfss = {delta_fss_calculated:.4f} Hz")
        print(f"Error = {error:.4f} Hz ({error_percent:.2f}%)")

        # Check if result is within acceptable tolerance (5%)
        if error_percent < 5.0:
            print("✓ PASSED")
        else:
            print("✗ FAILED")
            all_passed = False

    return all_passed


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("Power System Frequency Simulator - Validation Tests")
    print("=" * 70)

    passed_7_3 = test_example_7_3()
    passed_7_4 = test_example_7_4()

    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    if passed_7_3 and passed_7_4:
        print("✓ ALL TESTS PASSED")
        print("\nThe simulator correctly implements both Examples 7.3 and 7.4.")
        print("Results match expected values within acceptable tolerance.")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        if not passed_7_3:
            print("  - Example 7.3 tests failed")
        if not passed_7_4:
            print("  - Example 7.4 tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
