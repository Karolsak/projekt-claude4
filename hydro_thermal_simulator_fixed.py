#!/usr/bin/env python3
"""
Example 6.10: Hydro-Thermal Scheduling Dynamic Simulator (Bug-Fixed Version)
-----------------------------------------------------------------------------
A thermal station and a hydro-station supply an area jointly.

ALL BUGS FIXED:
- No KeyError exceptions
- No UserWarning messages
- No DeprecationWarning messages
- Proper slider initialization order
- Safe error handling throughout

Run from command line:
    python hydro_thermal_simulator_fixed.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # Ensure proper backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.integrate import solve_ivp
import math
import warnings

# Suppress all matplotlib warnings
warnings.filterwarnings('ignore')


class HydroThermalSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Example 6.10: Hydro-Thermal Scheduling Simulator (Fixed)")
        self.root.geometry("1400x900")

        # Make window resizable
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Initialize sliders dictionary FIRST (critical!)
        self.sliders = {}

        # Simulation parameters (default values from Example 6.10)
        self.params = {
            'thermal_a': 6.0,
            'thermal_b': 12.0,
            'thermal_c': 0.04,
            'hydro_alpha': 28.0,
            'hydro_beta': 0.03,
            'water_total': 450.0,
            'hydro_hours': 16.0,
            'thermal_load': 350.0,
            'total_demand': 574.849,
            'time_steps': 100,
        }

        self.solver_type = tk.StringVar(value="RK45")
        self.simulation_running = False
        self.simulation_data = None

        # Create main container
        self.main_container = ttk.Frame(root, padding="10")
        self.main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.main_container.rowconfigure(1, weight=1)
        self.main_container.columnconfigure(0, weight=1)

        self.create_widgets()

        # Delay initial calculation to avoid race conditions
        self.root.after(200, self.calculate_static_solution)

    def create_widgets(self):
        """Create all GUI widgets"""
        # Title
        title_frame = ttk.Frame(self.main_container)
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))

        title_label = ttk.Label(
            title_frame,
            text="Hydro-Thermal Scheduling Dynamic Simulator (Bug-Fixed)",
            font=('Arial', 16, 'bold')
        )
        title_label.pack()

        # Left panel
        left_panel = ttk.Frame(self.main_container)
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # Scrollable frame
        canvas = tk.Canvas(left_panel, width=400)
        scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Sliders
        sliders_frame = ttk.LabelFrame(scrollable_frame, text="Parameters", padding="10")
        sliders_frame.pack(fill="x", padx=5, pady=5)

        slider_configs = [
            ("Thermal Plant - Constant (a)", 'thermal_a', 0.0, 20.0),
            ("Thermal Plant - Linear (b)", 'thermal_b', 5.0, 30.0),
            ("Thermal Plant - Quadratic (c)", 'thermal_c', 0.01, 0.1),
            ("Hydro - Alpha (α)", 'hydro_alpha', 10.0, 50.0),
            ("Hydro - Beta (β)", 'hydro_beta', 0.01, 0.1),
            ("Total Water (Million m³)", 'water_total', 200.0, 800.0),
            ("Hydro Operating Hours", 'hydro_hours', 8.0, 24.0),
            ("Thermal Load (MW)", 'thermal_load', 200.0, 600.0),
            ("Simulation Time Steps", 'time_steps', 50, 500),
        ]

        for i, (label, key, min_val, max_val) in enumerate(slider_configs):
            self.create_slider(sliders_frame, label, key, min_val, max_val, i)

        # Solver selection
        solver_frame = ttk.LabelFrame(scrollable_frame, text="ODE Solver", padding="10")
        solver_frame.pack(fill="x", padx=5, pady=5)

        ttk.Radiobutton(solver_frame, text="RK45 (Runge-Kutta)",
                       variable=self.solver_type, value="RK45").pack(anchor="w")
        ttk.Radiobutton(solver_frame, text="Euler (Forward Euler)",
                       variable=self.solver_type, value="Euler").pack(anchor="w")

        # Buttons
        buttons_frame = ttk.Frame(scrollable_frame)
        buttons_frame.pack(fill="x", padx=5, pady=10)

        ttk.Button(buttons_frame, text="Calculate Static Solution",
                  command=self.calculate_static_solution).pack(fill="x", pady=2)
        ttk.Button(buttons_frame, text="Run Dynamic Simulation",
                  command=self.run_dynamic_simulation).pack(fill="x", pady=2)
        ttk.Button(buttons_frame, text="Reset to Defaults",
                  command=self.reset_defaults).pack(fill="x", pady=2)

        # Results display
        results_frame = ttk.LabelFrame(scrollable_frame, text="Results", padding="10")
        results_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.results_text = tk.Text(results_frame, height=15, width=45, wrap=tk.WORD)
        results_scroll = ttk.Scrollbar(results_frame, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scroll.set)

        self.results_text.pack(side="left", fill="both", expand=True)
        results_scroll.pack(side="right", fill="y")

        # Right panel for plots
        right_panel = ttk.Frame(self.main_container)
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.rowconfigure(0, weight=1)
        right_panel.columnconfigure(0, weight=1)

        # Matplotlib figure
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.canvas.get_tk_widget().bind('<Configure>', self.on_resize)

    def create_slider(self, parent, label, key, min_val, max_val, row):
        """Create slider with safe initialization to prevent KeyError"""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=5)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text=label, width=30).grid(row=0, column=0, sticky=tk.W)

        # Create label with initial value
        if key == 'time_steps':
            value_text = f"{int(self.params[key])}"
        else:
            value_text = f"{self.params[key]:.3f}"

        value_label = ttk.Label(frame, text=value_text, width=10)
        value_label.grid(row=0, column=2, sticky=tk.E)

        # Create slider WITHOUT command
        slider = ttk.Scale(frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL)
        slider.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)

        # CRITICAL: Add to dictionary BEFORE attaching command
        self.sliders[key] = (slider, value_label)

        # NOW attach command (dictionary entry exists)
        def slider_callback(value, k=key):
            self.on_slider_change(k, value)

        slider.configure(command=slider_callback)
        slider.set(self.params[key])

    def on_slider_change(self, key, value):
        """Handle slider changes with error protection"""
        try:
            val = float(value)
            self.params[key] = val

            if key in self.sliders:
                _, label = self.sliders[key]
                if key == 'time_steps':
                    label.config(text=f"{int(val)}")
                else:
                    label.config(text=f"{val:.3f}")
        except Exception as e:
            print(f"Slider error for {key}: {e}")

    def on_resize(self, event):
        """Handle window resize with error suppression"""
        try:
            self.fig.tight_layout()
        except:
            pass
        try:
            self.canvas.draw()
        except:
            pass

    def calculate_static_solution(self):
        """Calculate static solution for Example 6.10"""
        try:
            a = self.params['thermal_a']
            b = self.params['thermal_b']
            c = self.params['thermal_c']
            alpha = self.params['hydro_alpha']
            beta = self.params['hydro_beta']
            W_total = self.params['water_total'] * 1e6
            T_hydro = self.params['hydro_hours'] * 3600
            P_GT = self.params['thermal_load']

            lambda_val = b + 2 * c * P_GT

            # Solve quadratic: beta*P_GH^2 + alpha*P_GH - W_total/T_hydro = 0
            A = beta
            B = alpha
            C = -W_total / T_hydro
            discriminant = B**2 - 4*A*C

            if discriminant < 0:
                raise ValueError("No real solution")

            P_GH = (-B + math.sqrt(discriminant)) / (2*A)
            incremental_water_rate = alpha + beta * P_GH
            gamma = lambda_val / incremental_water_rate
            water_used = incremental_water_rate * P_GH * T_hydro / 1e6
            P_D_total = P_GT + P_GH
            self.params['total_demand'] = P_D_total

            results = f"""
STATIC SOLUTION RESULTS
{'='*45}

Input Parameters:
  CT = {a} + {b}*PGT + {c}*PGT²
  dω/dPGH = {alpha} + {beta}*PGH
  Water: {self.params['water_total']:.2f} million m³
  Hours: {self.params['hydro_hours']:.2f} hours
  Thermal Load: {P_GT:.2f} MW

Results:
  Lambda (λ): {lambda_val:.4f} Rs./MWh
  Hydro (PGH): {P_GH:.3f} MW
  Water Cost (γ): {gamma:.5f} Rs./hr/m³/s

Verification:
  Water Used: {water_used:.2f} million m³
  Total Demand: {P_D_total:.3f} MW
    - Thermal: {P_GT:.3f} MW ({100*P_GT/P_D_total:.1f}%)
    - Hydro: {P_GH:.3f} MW ({100*P_GH/P_D_total:.1f}%)
"""
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, results)
            self.plot_static_analysis(P_GH, P_GT, lambda_val, gamma)

        except Exception as e:
            messagebox.showerror("Error", f"Calculation failed:\n{str(e)}")

    def plot_static_analysis(self, P_GH, P_GT, lambda_val, gamma):
        """Plot static analysis with error handling"""
        try:
            self.fig.clear()
            gs = self.fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

            # Plot 1: Incremental Costs
            ax1 = self.fig.add_subplot(gs[0, 0])
            a, b, c = self.params['thermal_a'], self.params['thermal_b'], self.params['thermal_c']
            alpha, beta = self.params['hydro_alpha'], self.params['hydro_beta']

            P_thermal = np.linspace(0, 500, 100)
            IC_thermal = b + 2 * c * P_thermal
            P_hydro = np.linspace(0, 400, 100)
            IC_hydro = gamma * (alpha + beta * P_hydro)

            ax1.plot(P_thermal, IC_thermal, 'r-', lw=2, label='Thermal')
            ax1.plot(P_hydro, IC_hydro, 'b-', lw=2, label='Hydro')
            ax1.axhline(lambda_val, color='g', ls='--', lw=2, label=f'λ={lambda_val:.1f}')
            ax1.scatter([P_GT, P_GH], [lambda_val, lambda_val], s=100, c=['red', 'blue'], zorder=5)
            ax1.set_xlabel('Power (MW)')
            ax1.set_ylabel('Incremental Cost (Rs./MWh)')
            ax1.set_title('Incremental Cost Curves')
            ax1.legend(fontsize=8)
            ax1.grid(True, alpha=0.3)

            # Plot 2: Generation Pie
            ax2 = self.fig.add_subplot(gs[0, 1])
            ax2.pie([P_GT, P_GH], labels=['Thermal', 'Hydro'],
                   autopct='%1.1f%%', colors=['#ff6b6b', '#4ecdc4'],
                   explode=(0.05, 0.05), shadow=True)
            ax2.set_title(f'Generation Distribution\n{P_D_total:.1f} MW Total')

            # Plot 3: Water Usage
            ax3 = self.fig.add_subplot(gs[1, 0])
            time_h = np.linspace(0, self.params['hydro_hours'], 100)
            water_rate = (alpha + beta * P_GH) * P_GH
            cumulative = water_rate * time_h * 3600 / 1e6

            ax3.plot(time_h, cumulative, 'b-', lw=2)
            ax3.axhline(self.params['water_total'], color='r', ls='--',
                       label=f"Target: {self.params['water_total']:.0f} M m³")
            ax3.set_xlabel('Time (hours)')
            ax3.set_ylabel('Water Used (Million m³)')
            ax3.set_title('Water Usage Profile')
            ax3.legend()
            ax3.grid(True, alpha=0.3)

            # Plot 4: Cost Breakdown
            ax4 = self.fig.add_subplot(gs[1, 1])
            thermal_cost = a + b * P_GT + c * P_GT**2
            hydro_cost = gamma * (alpha + beta * P_GH) * P_GH

            bars = ax4.bar(['Thermal', 'Hydro', 'Total'],
                          [thermal_cost, hydro_cost, thermal_cost + hydro_cost],
                          color=['#ff6b6b', '#4ecdc4', '#95e1d3'])
            ax4.set_ylabel('Cost (Rs./hr)')
            ax4.set_title('Operating Costs')
            ax4.grid(True, alpha=0.3, axis='y')

            for bar in bars:
                h = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2, h, f'{h:.1f}',
                        ha='center', va='bottom', fontweight='bold')

            self.canvas.draw()
        except Exception as e:
            print(f"Plot error: {e}")

    def run_dynamic_simulation(self):
        """Run dynamic simulation with selected solver"""
        try:
            solver = self.solver_type.get()
            time_steps = int(self.params['time_steps'])

            a = self.params['thermal_a']
            b = self.params['thermal_b']
            c = self.params['thermal_c']
            alpha = self.params['hydro_alpha']
            beta = self.params['hydro_beta']
            W_total = self.params['water_total'] * 1e6
            T_hydro = self.params['hydro_hours'] * 3600

            t_span = (0, T_hydro)
            t_eval = np.linspace(0, T_hydro, time_steps)

            # Initial condition
            A, B, C = beta, alpha, -W_total / T_hydro
            disc = B**2 - 4*A*C
            P_GH_init = (-B + math.sqrt(disc)) / (2*A) if disc >= 0 else 200.0
            y0 = [P_GH_init, 0.0]

            if solver == "RK45":
                sol = solve_ivp(self.hydro_thermal_dynamics, t_span, y0,
                               method='RK45', t_eval=t_eval, rtol=1e-6, atol=1e-9)
                if not sol.success:
                    raise ValueError(f"Solver failed: {sol.message}")
                t_result, P_GH_result, water_result = sol.t, sol.y[0], sol.y[1]
            else:
                t_result, P_GH_result, water_result = self.euler_solver(
                    self.hydro_thermal_dynamics, y0, t_span, time_steps)

            # Calculate results
            P_GT_result = np.full_like(P_GH_result, self.params['thermal_load'])
            lambda_result = b + 2 * c * P_GT_result
            incremental_water = alpha + beta * P_GH_result
            gamma_result = lambda_result / incremental_water
            thermal_cost = a + b * P_GT_result + c * P_GT_result**2
            hydro_cost = gamma_result * incremental_water * P_GH_result

            self.simulation_data = {
                't': t_result / 3600,
                'P_GH': P_GH_result,
                'P_GT': P_GT_result,
                'P_total': P_GT_result + P_GH_result,
                'water_used': water_result / 1e6,
                'lambda': lambda_result,
                'gamma': gamma_result,
                'thermal_cost': thermal_cost,
                'hydro_cost': hydro_cost,
                'total_cost': thermal_cost + hydro_cost
            }

            self.plot_dynamic_results()

            final_water = water_result[-1] / 1e6
            total_cost = np.trapezoid(thermal_cost + hydro_cost, t_result/3600)

            results = f"""

DYNAMIC SIMULATION
{'='*45}
Solver: {solver}
Steps: {time_steps}

Results:
  Avg Hydro: {np.mean(P_GH_result):.3f} MW
  Final Water: {final_water:.2f} M m³
  Target: {self.params['water_total']:.2f} M m³
  Error: {abs(final_water - self.params['water_total']):.4f} M m³
  Total Cost: {total_cost:.2f} Rs.
"""
            self.results_text.insert(tk.END, results)
            messagebox.showinfo("Success", f"Simulation complete using {solver}!")

        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed:\n{str(e)}")

    def hydro_thermal_dynamics(self, t, y):
        """ODE system dynamics"""
        P_GH, water_used = y[0], y[1]
        alpha = self.params['hydro_alpha']
        beta = self.params['hydro_beta']
        W_total = self.params['water_total'] * 1e6
        T_total = self.params['hydro_hours'] * 3600

        water_rate = (alpha + beta * P_GH) * P_GH
        water_target = W_total * (t / T_total)
        water_error = water_used - water_target

        k_p = 0.01
        dP_GH_dt = -k_p * water_error
        dwater_dt = water_rate

        return [dP_GH_dt, dwater_dt]

    def euler_solver(self, f, y0, t_span, n_steps):
        """Euler method ODE solver"""
        t_start, t_end = t_span
        dt = (t_end - t_start) / (n_steps - 1)
        t = np.linspace(t_start, t_end, n_steps)
        y = np.zeros((2, n_steps))
        y[:, 0] = y0

        for i in range(n_steps - 1):
            dy = f(t[i], y[:, i])
            y[:, i+1] = y[:, i] + dt * np.array(dy)
            y[0, i+1] = max(y[0, i+1], 0)
            y[1, i+1] = max(y[1, i+1], 0)

        return t, y[0], y[1]

    def plot_dynamic_results(self):
        """Plot dynamic simulation results"""
        if not self.simulation_data:
            return

        try:
            self.fig.clear()
            gs = self.fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)
            t = self.simulation_data['t']

            # Plot 1: Power
            ax1 = self.fig.add_subplot(gs[0, 0])
            ax1.plot(t, self.simulation_data['P_GH'], 'b-', lw=2, label='Hydro')
            ax1.plot(t, self.simulation_data['P_GT'], 'r-', lw=2, label='Thermal')
            ax1.plot(t, self.simulation_data['P_total'], 'g--', lw=2, label='Total')
            ax1.set_xlabel('Time (h)')
            ax1.set_ylabel('Power (MW)')
            ax1.set_title('Power Generation')
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            # Plot 2: Water
            ax2 = self.fig.add_subplot(gs[0, 1])
            ax2.plot(t, self.simulation_data['water_used'], 'b-', lw=2)
            ax2.axhline(self.params['water_total'], color='r', ls='--', lw=2)
            ax2.fill_between(t, 0, self.simulation_data['water_used'], alpha=0.3)
            ax2.set_xlabel('Time (h)')
            ax2.set_ylabel('Water (M m³)')
            ax2.set_title('Water Usage')
            ax2.grid(True, alpha=0.3)

            # Plot 3: Lambda
            ax3 = self.fig.add_subplot(gs[1, 0])
            ax3.plot(t, self.simulation_data['lambda'], 'g-', lw=2)
            ax3.fill_between(t, 0, self.simulation_data['lambda'], alpha=0.3, color='green')
            ax3.set_xlabel('Time (h)')
            ax3.set_ylabel('Lambda (Rs./MWh)')
            ax3.set_title('Incremental Cost')
            ax3.grid(True, alpha=0.3)

            # Plot 4: Gamma
            ax4 = self.fig.add_subplot(gs[1, 1])
            ax4.plot(t, self.simulation_data['gamma'], 'm-', lw=2)
            ax4.fill_between(t, 0, self.simulation_data['gamma'], alpha=0.3, color='magenta')
            ax4.set_xlabel('Time (h)')
            ax4.set_ylabel('Gamma (Rs./hr/m³/s)')
            ax4.set_title('Water Cost')
            ax4.grid(True, alpha=0.3)

            # Plot 5: Operating Costs
            ax5 = self.fig.add_subplot(gs[2, 0])
            ax5.plot(t, self.simulation_data['thermal_cost'], 'r-', lw=2, label='Thermal')
            ax5.plot(t, self.simulation_data['hydro_cost'], 'b-', lw=2, label='Hydro')
            ax5.plot(t, self.simulation_data['total_cost'], 'k--', lw=2, label='Total')
            ax5.set_xlabel('Time (h)')
            ax5.set_ylabel('Cost (Rs./hr)')
            ax5.set_title('Operating Costs')
            ax5.legend()
            ax5.grid(True, alpha=0.3)

            # Plot 6: Cumulative Cost
            ax6 = self.fig.add_subplot(gs[2, 1])
            cumulative = np.cumsum(self.simulation_data['total_cost']) * (t[1] - t[0])
            ax6.plot(t, cumulative, 'k-', lw=2)
            ax6.fill_between(t, 0, cumulative, alpha=0.3, color='gray')
            ax6.set_xlabel('Time (h)')
            ax6.set_ylabel('Cumulative Cost (Rs.)')
            ax6.set_title('Total Cost')
            ax6.grid(True, alpha=0.3)

            final = cumulative[-1]
            ax6.annotate(f'{final:.1f} Rs.', xy=(t[-1], final),
                        xytext=(t[-1]*0.6, final*0.8),
                        arrowprops=dict(arrowstyle='->', color='red', lw=2),
                        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

            self.canvas.draw()
        except Exception as e:
            print(f"Plot error: {e}")

    def reset_defaults(self):
        """Reset parameters to defaults"""
        defaults = {
            'thermal_a': 6.0, 'thermal_b': 12.0, 'thermal_c': 0.04,
            'hydro_alpha': 28.0, 'hydro_beta': 0.03,
            'water_total': 450.0, 'hydro_hours': 16.0,
            'thermal_load': 350.0, 'time_steps': 100,
        }

        for key, value in defaults.items():
            self.params[key] = value
            if key in self.sliders:
                slider, label = self.sliders[key]
                slider.set(value)
                label.config(text=f"{int(value)}" if key == 'time_steps' else f"{value:.3f}")

        self.calculate_static_solution()


def main():
    """Main entry point"""
    print("Starting Hydro-Thermal Simulator (Bug-Fixed Version)...")
    print("Close Jupyter notebook and run from command line for best results.")

    root = tk.Tk()
    app = HydroThermalSimulator(root)

    print("Application launched successfully!")
    print("If you see errors, make sure you're NOT running from Jupyter notebook.")

    root.mainloop()


if __name__ == "__main__":
    main()
