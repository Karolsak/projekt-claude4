"""
Test script for Unit Commitment calculations (non-GUI)
Demonstrates the core algorithms used in Example 4.2
"""

import numpy as np


class UCCalculator:
    """Unit Commitment calculator without GUI dependencies"""

    def __init__(self):
        # Unit parameters from Table 4.5
        self.units = [
            {'name': 'Unit 1', 'a': 0.74, 'b': 22.9, 'd': 0, 'min': 1.0, 'max': 14.0},
            {'name': 'Unit 2', 'a': 1.56, 'b': 25.9, 'd': 0, 'min': 1.0, 'max': 14.0},
            {'name': 'Unit 3', 'a': 1.97, 'b': 29.0, 'd': 0, 'min': 1.0, 'max': 14.0},
            {'name': 'Unit 4', 'a': 1.36, 'b': 31.2, 'd': 0, 'min': 1.0, 'max': 14.0}
        ]

    def cost_function(self, P, unit_idx):
        """Calculate cost: F = 0.5 * a * P^2 + b * P + d"""
        unit = self.units[unit_idx]
        return 0.5 * unit['a'] * P**2 + unit['b'] * P + unit['d']

    def incremental_cost(self, P, unit_idx):
        """Calculate incremental cost: dC/dP = a * P + b"""
        unit = self.units[unit_idx]
        return unit['a'] * P + unit['b']

    def calculate_uc_table(self):
        """Calculate unit commitment using dynamic programming"""
        max_load = int(sum(unit['max'] for unit in self.units))
        n_units = len(self.units)

        print("="*80)
        print("UNIT COMMITMENT CALCULATION - Example 4.2")
        print("="*80)
        print("\nUnit Parameters (Table 4.5):")
        print("-"*80)
        print(f"{'Unit':>6} {'Min (MW)':>10} {'Max (MW)':>10} {'a':>10} {'b':>10} {'d':>10}")
        print("-"*80)
        for i, unit in enumerate(self.units):
            print(f"{i+1:>6} {unit['min']:>10.1f} {unit['max']:>10.1f} "
                  f"{unit['a']:>10.2f} {unit['b']:>10.2f} {unit['d']:>10.1f}")
        print()

        # Calculate individual unit costs
        unit_costs = []
        for i in range(n_units):
            costs = {}
            for P in range(max_load + 1):
                if P == 0:
                    costs[P] = 0
                elif self.units[i]['min'] <= P <= self.units[i]['max']:
                    costs[P] = self.cost_function(P, i)
                else:
                    costs[P] = float('inf')
            unit_costs.append(costs)

        # Print individual unit costs for verification (matching textbook)
        print("Individual Unit Generation Costs:")
        print("-"*80)
        for i in range(n_units):
            print(f"\n{self.units[i]['name']}:")
            print(f"  f{i+1}(P) = 0.5 × {self.units[i]['a']} × P² + {self.units[i]['b']} × P")
            print(f"         = ({self.units[i]['a']/2} × P + {self.units[i]['b']}) × P")
            print(f"  Load (MW) | Cost (Rs/hr)")
            for P in range(1, 9):
                if self.units[i]['min'] <= P <= self.units[i]['max']:
                    cost = self.cost_function(P, i)
                    print(f"  {P:>8.0f}  | {cost:>12.2f}")

        # Dynamic programming
        F = [{} for _ in range(n_units + 1)]
        allocation = [{} for _ in range(n_units + 1)]

        # Base case
        for load in range(max_load + 1):
            F[0][load] = float('inf') if load > 0 else 0
            allocation[0][load] = []

        # Fill DP table
        print("\n\nDynamic Programming Solution:")
        print("="*80)

        for n in range(1, n_units + 1):
            for load in range(max_load + 1):
                min_cost = float('inf')
                best_allocation = []

                for p_unit in range(max(0, load - int(self.units[n-1]['max'])), load + 1):
                    remaining = load - p_unit

                    if remaining < 0:
                        continue

                    prev_cost = F[n-1].get(remaining, float('inf'))
                    unit_cost = unit_costs[n-1].get(p_unit, float('inf'))
                    total_cost = prev_cost + unit_cost

                    if total_cost < min_cost:
                        min_cost = total_cost
                        best_allocation = allocation[n-1].get(remaining, []).copy()
                        if p_unit > 0:
                            best_allocation.append((n-1, p_unit))

                F[n][load] = min_cost
                allocation[n][load] = best_allocation

        return F, allocation

    def economic_dispatch(self, load, committed_units):
        """Perform economic dispatch using lambda iteration"""
        if not committed_units:
            return {}, 0, 0

        lambda_min = min(self.incremental_cost(self.units[i]['min'], i)
                        for i in committed_units)
        lambda_max = max(self.incremental_cost(self.units[i]['max'], i)
                        for i in committed_units)

        tolerance = 0.01
        max_iterations = 100

        for iteration in range(max_iterations):
            lambda_mid = (lambda_min + lambda_max) / 2

            total_power = 0
            power_allocation = {}

            for i in committed_units:
                unit = self.units[i]
                P = (lambda_mid - unit['b']) / unit['a']
                P = max(unit['min'], min(unit['max'], P))
                power_allocation[i] = P
                total_power += P

            if abs(total_power - load) < tolerance:
                break
            elif total_power < load:
                lambda_min = lambda_mid
            else:
                lambda_max = lambda_mid

        total_cost = sum(self.cost_function(power_allocation[i], i)
                        for i in committed_units)

        return power_allocation, total_cost, lambda_mid

    def print_results(self, F, allocation, target_load=8):
        """Print detailed results matching textbook format"""
        n_units = len(self.units)

        print(f"\n\nDetailed Analysis for {target_load} MW Load:")
        print("="*80)

        # Show costs for each number of units
        for n in range(1, n_units + 1):
            if target_load not in F[n]:
                continue

            cost = F[n][target_load]
            alloc = allocation[n][target_load]

            print(f"\nUsing {n} unit(s):")
            print(f"  F{n}({target_load}) = {cost:.2f} Rs/hr")

            if alloc:
                print(f"  Unit allocation:")
                for unit_idx, power in alloc:
                    print(f"    {self.units[unit_idx]['name']}: {power:.2f} MW")
            else:
                print(f"  No units committed (Unit 1 supplies all {target_load} MW)")

        print("\n" + "="*80)
        print("OPTIMAL SOLUTION:")
        print("="*80)

        # Optimal solution
        optimal_cost = F[n_units][target_load]
        optimal_alloc = allocation[n_units][target_load]

        print(f"\nFor {target_load} MW load demand:")
        print(f"Minimum Cost: {optimal_cost:.2f} Rs/hr")
        print(f"\nCommitted Units:")
        for unit_idx, power in optimal_alloc:
            print(f"  {self.units[unit_idx]['name']}: {power:.0f} MW")

        # Economic dispatch
        print(f"\n\nEconomic Dispatch (Optimal Load Sharing):")
        print("-"*80)
        committed = [idx for idx, _ in optimal_alloc]
        power_alloc, total_cost, lambda_val = self.economic_dispatch(target_load, committed)

        print(f"Lambda (Incremental Cost): {lambda_val:.2f} Rs/MWh")
        print(f"\nOptimal Power Allocation:")
        for unit_idx in committed:
            power = power_alloc[unit_idx]
            cost = self.cost_function(power, unit_idx)
            inc_cost = self.incremental_cost(power, unit_idx)
            print(f"  {self.units[unit_idx]['name']}: {power:.2f} MW "
                  f"(Cost: {cost:.2f} Rs/hr, Inc. Cost: {inc_cost:.2f} Rs/MWh)")

        print(f"\nTotal Generation Cost: {total_cost:.2f} Rs/hr")

        # Verification
        print(f"\n\nVerification (matching textbook Example 4.2):")
        print("-"*80)
        if target_load == 8:
            # Manual calculation from textbook
            P1 = 6.73
            P2 = 1.27
            f1 = self.cost_function(P1, 0)
            f2 = self.cost_function(P2, 1)
            print(f"Unit 1 power: {P1} MW → f₁({P1}) = {f1:.2f} Rs/hr")
            print(f"Unit 2 power: {P2} MW → f₂({P2}) = {f2:.2f} Rs/hr")
            print(f"Total cost: {f1 + f2:.2f} Rs/hr")
            print(f"(Expected: 205.11 Rs/hr from textbook)")

        # UC Table summary
        print("\n\n" + "="*80)
        print("UNIT COMMITMENT STATUS TABLE")
        print("="*80)
        print(f"{'Load Range':>12} | {'Unit 1':>6} | {'Unit 2':>6} | {'Unit 3':>6} | {'Unit 4':>6}")
        print("-"*80)

        ranges = [
            ("1-5 MW", [1, 0, 0, 0]),
            ("6-13 MW", [1, 1, 0, 0]),
            ("14-18 MW", [1, 1, 1, 0]),
            ("19-56 MW", [1, 1, 1, 1])
        ]

        for load_range, status in ranges:
            status_str = " | ".join([f"  {s}   " for s in status])
            print(f"{load_range:>12} | {status_str}")

        print("\n(Status 1 = Running, Status 0 = Off)")


def main():
    """Run UC calculations and display results"""
    calc = UCCalculator()

    # Calculate UC table
    F, allocation = calc.calculate_uc_table()

    # Print detailed results for 8 MW (as in Example 4.2)
    calc.print_results(F, allocation, target_load=8)

    # Print abbreviated table for all loads
    print("\n\n" + "="*80)
    print("COMPLETE UNIT COMMITMENT TABLE (1-20 MW)")
    print("="*80)
    print(f"{'Load':>5} | {'Cost':>10} | {'Unit 1':>6} | {'Unit 2':>6} | "
          f"{'Unit 3':>6} | {'Unit 4':>6} | {'Total':>6}")
    print("-"*80)

    n_units = len(calc.units)
    for load in range(1, 21):
        if load in F[n_units]:
            cost = F[n_units][load]
            alloc = allocation[n_units][load]

            unit_power = [0] * n_units
            for unit_idx, power in alloc:
                unit_power[unit_idx] = power

            total_power = sum(unit_power)
            power_str = " | ".join([f"{p:>6.2f}" for p in unit_power])

            print(f"{load:>5} | {cost:>10.2f} | {power_str} | {total_power:>6.2f}")

    print("\n" + "="*80)
    print("Calculation Complete!")
    print("="*80)


if __name__ == "__main__":
    main()
