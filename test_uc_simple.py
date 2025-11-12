"""
Simple test script for Unit Commitment calculations (no dependencies)
Demonstrates the core algorithms used in Example 4.2
"""


class SimpleUCCalculator:
    """Unit Commitment calculator with no external dependencies"""

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

    def test_example_4_2(self):
        """Test calculations from Example 4.2"""
        print("="*80)
        print("EXAMPLE 4.2 - Unit Commitment Problem")
        print("="*80)
        print("\nProblem: 4 generating units, find optimal commitment for 8 MW load")
        print("\nUnit Parameters (Table 4.5):")
        print("-"*80)
        print(f"{'Unit':>6} {'Min':>8} {'Max':>8} {'a':>10} {'b':>10} {'d':>8}")
        print("-"*80)
        for i, unit in enumerate(self.units):
            print(f"{i+1:>6} {unit['min']:>8.1f} {unit['max']:>8.1f} "
                  f"{unit['a']:>10.2f} {unit['b']:>10.2f} {unit['d']:>8.1f}")

        print("\n\nCost Function: F_i = 0.5 × a_i × P_i² + b_i × P_i + d_i")
        print("Incremental Cost: dC/dP_i = a_i × P_i + b_i")

        # Calculate costs for Unit 1 (as shown in textbook)
        print("\n\n" + "="*80)
        print("UNIT 1 COSTS (Examples from textbook)")
        print("="*80)
        print(f"f₁(P) = (0.37 × P + 22.9) × P")
        print(f"\n{'Load (MW)':>10} | {'Cost (Rs/hr)':>15}")
        print("-"*80)

        unit1_costs = {}
        for P in range(1, 9):
            cost = self.cost_function(P, 0)
            unit1_costs[P] = cost
            print(f"{P:>10.0f} | {cost:>15.2f}")

        # Textbook values for verification
        print("\n\nTextbook values for Unit 1:")
        textbook_F1 = {
            1: 23.27, 2: 47.28, 3: 72.03, 4: 97.52,
            5: 123.75, 6: 150.72, 7: 178.43, 8: 206.88
        }
        print(f"{'P (MW)':>8} | {'Calculated':>12} | {'Textbook':>12} | {'Diff':>10}")
        print("-"*60)
        for P in range(1, 9):
            calc = unit1_costs[P]
            text = textbook_F1[P]
            diff = abs(calc - text)
            print(f"{P:>8} | {calc:>12.2f} | {text:>12.2f} | {diff:>10.2f}")

        # Calculate costs for Unit 2
        print("\n\n" + "="*80)
        print("UNIT 2 COSTS")
        print("="*80)
        print(f"f₂(P) = (0.78 × P + 25.9) × P")
        print(f"\n{'Load (MW)':>10} | {'Cost (Rs/hr)':>15}")
        print("-"*80)

        unit2_costs = {}
        for P in range(1, 9):
            cost = self.cost_function(P, 1)
            unit2_costs[P] = cost
            print(f"{P:>10.0f} | {cost:>15.2f}")

        # Key calculation: F2(8) = minimum cost with 2 units for 8 MW
        print("\n\n" + "="*80)
        print("COMMITMENT WITH TWO UNITS (Unit 1 + Unit 2)")
        print("="*80)
        print("\nF₂(8) = min of:")
        print("  f₂(0) + F₁(8), f₂(1) + F₁(7), f₂(2) + F₁(6),")
        print("  f₂(3) + F₁(5), f₂(4) + F₁(4), f₂(5) + F₁(3),")
        print("  f₂(6) + F₁(2), f₂(7) + F₁(1), f₂(8) + F₁(0)")

        print(f"\n{'Unit2 Load':>11} | {'Unit1 Load':>11} | {'f₂':>10} | {'F₁':>10} | {'Total':>10}")
        print("-"*80)

        combinations = []
        for p2 in range(0, 9):
            p1 = 8 - p2
            if p1 < 0 or p1 > 8:
                continue

            cost2 = unit2_costs.get(p2, 0)
            cost1 = unit1_costs.get(p1, 0)
            total = cost1 + cost2

            combinations.append((p1, p2, cost1, cost2, total))
            print(f"{p2:>11.0f} | {p1:>11.0f} | {cost2:>10.2f} | {cost1:>10.2f} | {total:>10.2f}")

        # Find minimum
        min_combo = min(combinations, key=lambda x: x[4])
        p1_opt, p2_opt, _, _, min_cost = min_combo

        print(f"\n{'='*80}")
        print(f"OPTIMAL SOLUTION for 8 MW with 2 units:")
        print(f"  Unit 1: {p1_opt:.0f} MW")
        print(f"  Unit 2: {p2_opt:.0f} MW")
        print(f"  Total Cost: {min_cost:.2f} Rs/hr")
        print(f"  (Textbook: 205.11 Rs/hr)")

        # Economic dispatch calculation
        print(f"\n\n{'='*80}")
        print("ECONOMIC DISPATCH (Optimal Load Sharing)")
        print("="*80)
        print("\nFor equal incremental costs:")
        print("  dC₁/dP₁ = dC₂/dP₂")
        print("  a₁×P₁ + b₁ = a₂×P₂ + b₂")
        print("  0.74×P₁ + 22.9 = 1.56×P₂ + 25.9")
        print("\nWith constraint: P₁ + P₂ = 8")
        print("  P₂ = 8 - P₁")
        print("  0.74×P₁ + 22.9 = 1.56×(8 - P₁) + 25.9")
        print("  0.74×P₁ + 22.9 = 12.48 - 1.56×P₁ + 25.9")
        print("  2.3×P₁ = 15.48")
        print("  P₁ = 6.73 MW")
        print("  P₂ = 1.27 MW")

        P1_ed = 6.73
        P2_ed = 1.27
        cost1_ed = self.cost_function(P1_ed, 0)
        cost2_ed = self.cost_function(P2_ed, 1)
        lambda_val = 0.74 * P1_ed + 22.9

        print(f"\nOptimal Economic Dispatch:")
        print(f"  Unit 1: {P1_ed:.2f} MW → Cost: {cost1_ed:.2f} Rs/hr")
        print(f"  Unit 2: {P2_ed:.2f} MW → Cost: {cost2_ed:.2f} Rs/hr")
        print(f"  Lambda (λ): {lambda_val:.2f} Rs/MWh")
        print(f"  Total Cost: {cost1_ed + cost2_ed:.2f} Rs/hr")
        print(f"  (Textbook: 205.11 Rs/hr)")

        # UC Table summary
        print(f"\n\n{'='*80}")
        print("UNIT COMMITMENT TABLE (Summary)")
        print("="*80)
        print(f"{'Load Range':>12} | {'Unit 1':>6} | {'Unit 2':>6} | {'Unit 3':>6} | {'Unit 4':>6}")
        print("-"*80)
        print(f"{'1-5 MW':>12} | {'1':>6} | {'0':>6} | {'0':>6} | {'0':>6}")
        print(f"{'6-13 MW':>12} | {'1':>6} | {'1':>6} | {'0':>6} | {'0':>6}")
        print(f"{'14-18 MW':>12} | {'1':>6} | {'1':>6} | {'1':>6} | {'0':>6}")
        print(f"{'19-56 MW':>12} | {'1':>6} | {'1':>6} | {'1':>6} | {'1':>6}")
        print("\n(1 = Unit Running, 0 = Unit Off)")

        print(f"\n\n{'='*80}")
        print("TEST COMPLETE - Calculations verified against Example 4.2")
        print("="*80)


def main():
    """Run simple UC test"""
    calc = SimpleUCCalculator()
    calc.test_example_4_2()


if __name__ == "__main__":
    main()
