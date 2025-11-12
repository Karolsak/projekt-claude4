"""
Example 6.10: Hydro-Thermal Scheduling Dynamic Simulator
---------------------------------------------------------
A thermal station and a hydro-station supply an area jointly.
Features:
- Dynamic simulation with RK45 and Euler ODE solvers
- Interactive sliders for parameter adjustment
- Real-time visualization with dynamic graphs
- Automatic window resizing
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.integrate import solve_ivp
import math


class HydroThermalSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Example 6.10: Hydro-Thermal Scheduling Simulator")
        self.root.geometry("1400x900")

        # Make window resizable
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Simulation parameters (default values from Example 6.10)
        self.params = {
            'thermal_a': 6.0,      # Constant term in CT
            'thermal_b': 12.0,     # Linear term in CT
            'thermal_c': 0.04,     # Quadratic term in CT
            'hydro_alpha': 28.0,   # Constant in incremental water rate
            'hydro_beta': 0.03,    # Linear term in incremental water rate
            'water_total': 450.0,  # Million m³
            'hydro_hours': 16.0,   # Operating hours
            'thermal_load': 350.0, # MW when both plants operate
            'total_demand': 574.849, # Total load (will be calculated)
            'time_steps': 100,     # Number of simulation steps
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
        self.calculate_static_solution()

    def create_widgets(self):
        """Create all GUI widgets"""

        # Title
        title_frame = ttk.Frame(self.main_container)
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))

        title_label = ttk.Label(
            title_frame,
            text="Hydro-Thermal Scheduling Dynamic Simulator",
            font=('Arial', 16, 'bold')
        )
        title_label.pack()

        # Create left panel for controls
        left_panel = ttk.Frame(self.main_container)
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # Create scrollable frame for sliders
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

        # Sliders frame
        sliders_frame = ttk.LabelFrame(scrollable_frame, text="Parameters", padding="10")
        sliders_frame.pack(fill="x", padx=5, pady=5)

        self.sliders = {}
        slider_configs = [
            ("Thermal Plant - Constant (a)", 'thermal_a', 0.0, 20.0, 0.1),
            ("Thermal Plant - Linear (b)", 'thermal_b', 5.0, 30.0, 0.5),
            ("Thermal Plant - Quadratic (c)", 'thermal_c', 0.01, 0.1, 0.001),
            ("Hydro - Alpha (α)", 'hydro_alpha', 10.0, 50.0, 0.5),
            ("Hydro - Beta (β)", 'hydro_beta', 0.01, 0.1, 0.001),
            ("Total Water (Million m³)", 'water_total', 200.0, 800.0, 10.0),
            ("Hydro Operating Hours", 'hydro_hours', 8.0, 24.0, 0.5),
            ("Thermal Load (MW)", 'thermal_load', 200.0, 600.0, 10.0),
            ("Simulation Time Steps", 'time_steps', 50, 500, 10),
        ]

        for i, (label, key, min_val, max_val, resolution) in enumerate(slider_configs):
            self.create_slider(sliders_frame, label, key, min_val, max_val, resolution, i)

        # Solver selection
        solver_frame = ttk.LabelFrame(scrollable_frame, text="ODE Solver", padding="10")
        solver_frame.pack(fill="x", padx=5, pady=5)

        ttk.Radiobutton(
            solver_frame,
            text="RK45 (Runge-Kutta 4th/5th order)",
            variable=self.solver_type,
            value="RK45"
        ).pack(anchor="w")

        ttk.Radiobutton(
            solver_frame,
            text="Euler (Forward Euler method)",
            variable=self.solver_type,
            value="Euler"
        ).pack(anchor="w")

        # Control buttons
        buttons_frame = ttk.Frame(scrollable_frame)
        buttons_frame.pack(fill="x", padx=5, pady=10)

        ttk.Button(
            buttons_frame,
            text="Calculate Static Solution",
            command=self.calculate_static_solution
        ).pack(fill="x", pady=2)

        ttk.Button(
            buttons_frame,
            text="Run Dynamic Simulation",
            command=self.run_dynamic_simulation
        ).pack(fill="x", pady=2)

        ttk.Button(
            buttons_frame,
            text="Reset to Defaults",
            command=self.reset_defaults
        ).pack(fill="x", pady=2)

        # Results display
        results_frame = ttk.LabelFrame(scrollable_frame, text="Static Solution Results", padding="10")
        results_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.results_text = tk.Text(results_frame, height=15, width=45, wrap=tk.WORD)
        results_scroll = ttk.Scrollbar(results_frame, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scroll.set)

        self.results_text.pack(side="left", fill="both", expand=True)
        results_scroll.pack(side="right", fill="y")

        # Create right panel for plots
        right_panel = ttk.Frame(self.main_container)
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.rowconfigure(0, weight=1)
        right_panel.columnconfigure(0, weight=1)

        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure resizing
        self.canvas.get_tk_widget().bind('<Configure>', self.on_resize)

    def create_slider(self, parent, label, key, min_val, max_val, resolution, row):
        """Create a labeled slider"""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=5)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text=label, width=30).grid(row=0, column=0, sticky=tk.W)

        # Create value label first
        value_label = ttk.Label(frame, text=f"{self.params[key]:.3f}", width=10)
        value_label.grid(row=0, column=2, sticky=tk.E)

        # Create slider (command will be set after adding to dict)
        slider = ttk.Scale(
            frame,
            from_=min_val,
            to=max_val,
            orient=tk.HORIZONTAL
        )
        slider.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)

        # Add to dictionary BEFORE setting command and value
        self.sliders[key] = (slider, value_label)

        # Now set the command and value
        slider.configure(command=lambda v, k=key: self.on_slider_change(k, v))
        slider.set(self.params[key])

    def on_slider_change(self, key, value):
        """Handle slider value changes"""
        val = float(value)
        self.params[key] = val
        _, label = self.sliders[key]

        if key == 'time_steps':
            label.config(text=f"{int(val)}")
        else:
            label.config(text=f"{val:.3f}")

    def on_resize(self, event):
        """Handle window resize events"""
        try:
            self.fig.tight_layout()
        except Exception:
            # Ignore tight_layout errors (happens with some plot types like pie charts)
            pass
        self.canvas.draw()

    def calculate_static_solution(self):
        """Calculate the static solution for Example 6.10"""
        try:
            # Extract parameters
            a = self.params['thermal_a']
            b = self.params['thermal_b']
            c = self.params['thermal_c']
            alpha = self.params['hydro_alpha']
            beta = self.params['hydro_beta']
            W_total = self.params['water_total'] * 1e6  # Convert to m³
            T_hydro = self.params['hydro_hours'] * 3600  # Convert to seconds
            P_GT = self.params['thermal_load']

            # Calculate lambda (incremental cost)
            lambda_val = b + 2 * c * P_GT

            # Solve quadratic equation for hydro power
            # Water constraint: (alpha + beta*P_GH) * P_GH * T_hydro = W_total
            # beta*P_GH^2 + alpha*P_GH - W_total/T_hydro = 0

            A = beta
            B = alpha
            C = -W_total / T_hydro

            discriminant = B**2 - 4*A*C

            if discriminant < 0:
                raise ValueError("No real solution exists for the given parameters")

            P_GH_1 = (-B + math.sqrt(discriminant)) / (2*A)
            P_GH_2 = (-B - math.sqrt(discriminant)) / (2*A)

            # Take positive solution
            P_GH = P_GH_1 if P_GH_1 > 0 else P_GH_2

            # Calculate water cost
            incremental_water_rate = alpha + beta * P_GH
            gamma = lambda_val / incremental_water_rate

            # Calculate total water used (verification)
            water_used = incremental_water_rate * P_GH * T_hydro / 1e6  # Million m³

            # Calculate total demand
            P_D_total = P_GT + P_GH

            # Update params
            self.params['total_demand'] = P_D_total

            # Display results
            results = f"""
STATIC SOLUTION RESULTS
{'='*45}

Input Parameters:
------------------
Thermal Cost Function:
  CT = {a} + {b}*PGT + {c}*PGT²

Hydro Water Rate Function:
  dω/dPGH = {alpha} + {beta}*PGH

Total Water Available: {self.params['water_total']:.2f} million m³
Hydro Operating Hours: {self.params['hydro_hours']:.2f} hours
Thermal Load (given): {P_GT:.2f} MW

Calculated Results:
------------------
Lambda (λ): {lambda_val:.4f} Rs./MWh
Hydro Generation (PGH): {P_GH:.3f} MW
Incremental Water Rate: {incremental_water_rate:.4f} m³/s
Water Cost (γ): {gamma:.5f} Rs./hr/m³/s

Verification:
------------------
Water Used: {water_used:.2f} million m³
Water Available: {self.params['water_total']:.2f} million m³
Difference: {abs(water_used - self.params['water_total']):.6f} million m³

Total Demand: {P_D_total:.3f} MW
  - Thermal: {P_GT:.3f} MW ({100*P_GT/P_D_total:.1f}%)
  - Hydro: {P_GH:.3f} MW ({100*P_GH/P_D_total:.1f}%)

Economic Analysis:
------------------
Thermal Generation Cost: {a + b*P_GT + c*P_GT**2:.2f} Rs./hr
Hydro Water Cost: {gamma * incremental_water_rate * P_GH:.2f} Rs./hr
Total Operating Cost: {a + b*P_GT + c*P_GT**2 + gamma * incremental_water_rate * P_GH:.2f} Rs./hr
"""

            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, results)

            # Plot static results
            self.plot_static_analysis(P_GH, P_GT, lambda_val, gamma)

        except Exception as e:
            messagebox.showerror("Calculation Error", f"Error in calculation:\n{str(e)}")

    def plot_static_analysis(self, P_GH, P_GT, lambda_val, gamma):
        """Plot static analysis results"""
        self.fig.clear()

        # Create 2x2 subplot grid
        gs = self.fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # Plot 1: Incremental Cost Curves
        ax1 = self.fig.add_subplot(gs[0, 0])

        a = self.params['thermal_a']
        b = self.params['thermal_b']
        c = self.params['thermal_c']
        alpha = self.params['hydro_alpha']
        beta = self.params['hydro_beta']

        P_range_thermal = np.linspace(0, 500, 100)
        IC_thermal = b + 2 * c * P_range_thermal

        P_range_hydro = np.linspace(0, 400, 100)
        IC_hydro = gamma * (alpha + beta * P_range_hydro)

        ax1.plot(P_range_thermal, IC_thermal, 'r-', linewidth=2, label='Thermal IC')
        ax1.plot(P_range_hydro, IC_hydro, 'b-', linewidth=2, label='Hydro IC (γ adjusted)')
        ax1.axhline(y=lambda_val, color='g', linestyle='--', linewidth=2, label=f'λ = {lambda_val:.2f}')
        ax1.axvline(x=P_GT, color='r', linestyle=':', alpha=0.5)
        ax1.axvline(x=P_GH, color='b', linestyle=':', alpha=0.5)
        ax1.scatter([P_GT], [lambda_val], color='red', s=100, zorder=5, label=f'PGT = {P_GT:.1f} MW')
        ax1.scatter([P_GH], [lambda_val], color='blue', s=100, zorder=5, label=f'PGH = {P_GH:.1f} MW')
        ax1.set_xlabel('Power Generation (MW)')
        ax1.set_ylabel('Incremental Cost (Rs./MWh)')
        ax1.set_title('Incremental Cost Characteristics')
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)

        # Plot 2: Generation Distribution
        ax2 = self.fig.add_subplot(gs[0, 1])

        labels = ['Thermal', 'Hydro']
        sizes = [P_GT, P_GH]
        colors = ['#ff6b6b', '#4ecdc4']
        explode = (0.05, 0.05)

        ax2.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=90)
        ax2.set_title(f'Power Generation Distribution\nTotal: {P_GT + P_GH:.1f} MW')

        # Plot 3: Water Usage Over Time (constant for static)
        ax3 = self.fig.add_subplot(gs[1, 0])

        time_hours = np.linspace(0, self.params['hydro_hours'], 100)
        water_rate = (alpha + beta * P_GH) * P_GH  # m³/s
        cumulative_water = water_rate * time_hours * 3600 / 1e6  # Million m³

        ax3.plot(time_hours, cumulative_water, 'b-', linewidth=2)
        ax3.axhline(y=self.params['water_total'], color='r', linestyle='--',
                    label=f'Total Available: {self.params["water_total"]:.1f} M m³')
        ax3.set_xlabel('Time (hours)')
        ax3.set_ylabel('Cumulative Water Used (Million m³)')
        ax3.set_title('Water Usage Profile (Static)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Plot 4: Cost Comparison
        ax4 = self.fig.add_subplot(gs[1, 1])

        thermal_cost = a + b * P_GT + c * P_GT**2
        hydro_cost = gamma * (alpha + beta * P_GH) * P_GH

        categories = ['Thermal\nGeneration', 'Hydro\nWater', 'Total']
        costs = [thermal_cost, hydro_cost, thermal_cost + hydro_cost]
        colors_bar = ['#ff6b6b', '#4ecdc4', '#95e1d3']

        bars = ax4.bar(categories, costs, color=colors_bar, edgecolor='black', linewidth=1.5)
        ax4.set_ylabel('Cost (Rs./hr)')
        ax4.set_title('Operating Cost Breakdown')
        ax4.grid(True, alpha=0.3, axis='y')

        # Add value labels on bars
        for bar, cost in zip(bars, costs):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{cost:.1f}',
                    ha='center', va='bottom', fontweight='bold')

        self.canvas.draw()

    def run_dynamic_simulation(self):
        """Run dynamic simulation with selected ODE solver"""
        try:
            solver = self.solver_type.get()
            time_steps = int(self.params['time_steps'])

            # Time span (16 hours for hydro operation)
            t_span = (0, self.params['hydro_hours'] * 3600)  # seconds
            t_eval = np.linspace(t_span[0], t_span[1], time_steps)

            # Initial conditions: [P_GH, water_used]
            # Start with estimated hydro power from static solution
            a = self.params['thermal_a']
            b = self.params['thermal_b']
            c = self.params['thermal_c']
            alpha = self.params['hydro_alpha']
            beta = self.params['hydro_beta']
            W_total = self.params['water_total'] * 1e6
            T_hydro = self.params['hydro_hours'] * 3600

            # Initial guess for P_GH
            A = beta
            B = alpha
            C = -W_total / T_hydro
            discriminant = B**2 - 4*A*C
            P_GH_initial = (-B + math.sqrt(discriminant)) / (2*A) if discriminant >= 0 else 200.0

            y0 = [P_GH_initial, 0.0]  # [P_GH, cumulative_water_used]

            if solver == "RK45":
                # Use scipy's RK45 solver
                sol = solve_ivp(
                    self.hydro_thermal_dynamics,
                    t_span,
                    y0,
                    method='RK45',
                    t_eval=t_eval,
                    rtol=1e-6,
                    atol=1e-9
                )

                if not sol.success:
                    raise ValueError(f"RK45 solver failed: {sol.message}")

                t_result = sol.t
                P_GH_result = sol.y[0]
                water_used_result = sol.y[1]

            else:  # Euler method
                t_result, P_GH_result, water_used_result = self.euler_solver(
                    self.hydro_thermal_dynamics,
                    y0,
                    t_span,
                    time_steps
                )

            # Calculate thermal power and other variables
            P_GT_result = np.full_like(P_GH_result, self.params['thermal_load'])
            P_total_result = P_GT_result + P_GH_result

            # Calculate lambda over time
            lambda_result = b + 2 * c * P_GT_result

            # Calculate water cost over time
            incremental_water_rate = alpha + beta * P_GH_result
            gamma_result = lambda_result / incremental_water_rate

            # Calculate costs
            thermal_cost_result = a + b * P_GT_result + c * P_GT_result**2
            hydro_cost_result = gamma_result * incremental_water_rate * P_GH_result

            # Store simulation data
            self.simulation_data = {
                't': t_result / 3600,  # Convert to hours
                'P_GH': P_GH_result,
                'P_GT': P_GT_result,
                'P_total': P_total_result,
                'water_used': water_used_result / 1e6,  # Convert to million m³
                'lambda': lambda_result,
                'gamma': gamma_result,
                'thermal_cost': thermal_cost_result,
                'hydro_cost': hydro_cost_result,
                'total_cost': thermal_cost_result + hydro_cost_result
            }

            # Plot dynamic results
            self.plot_dynamic_results()

            # Update results text
            final_water = water_used_result[-1] / 1e6
            avg_P_GH = np.mean(P_GH_result)
            avg_gamma = np.mean(gamma_result)

            results_append = f"""

DYNAMIC SIMULATION RESULTS
{'='*45}

Solver: {solver}
Time Steps: {time_steps}

Final State:
------------------
Average Hydro Power: {avg_P_GH:.3f} MW
Final Water Used: {final_water:.2f} million m³
Water Target: {self.params['water_total']:.2f} million m³
Water Error: {abs(final_water - self.params['water_total']):.4f} million m³

Average Water Cost: {avg_gamma:.5f} Rs./hr/m³/s
Average Lambda: {np.mean(lambda_result):.4f} Rs./MWh

Total Operating Cost: {np.trapezoid(thermal_cost_result + hydro_cost_result, t_result/3600):.2f} Rs.
"""

            current_text = self.results_text.get(1.0, tk.END)
            self.results_text.insert(tk.END, results_append)

            messagebox.showinfo("Simulation Complete",
                              f"Dynamic simulation completed successfully using {solver} solver!")

        except Exception as e:
            messagebox.showerror("Simulation Error", f"Error in dynamic simulation:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def hydro_thermal_dynamics(self, t, y):
        """
        Define the dynamics of the hydro-thermal system

        State variables:
        y[0] = P_GH (hydro power generation)
        y[1] = cumulative water used (m³)

        The system adjusts hydro power to maintain optimal dispatch
        while respecting water constraints.
        """
        P_GH = y[0]
        water_used = y[1]

        # Parameters
        alpha = self.params['hydro_alpha']
        beta = self.params['hydro_beta']
        W_total = self.params['water_total'] * 1e6
        T_total = self.params['hydro_hours'] * 3600

        # Water usage rate (m³/s)
        water_rate = (alpha + beta * P_GH) * P_GH

        # Remaining time
        t_remaining = max(T_total - t, 1.0)

        # Target water usage based on time
        water_target = W_total * (t / T_total)

        # Adjust hydro power based on water constraint
        # If using too much water, reduce power; if using too little, increase power
        water_error = water_used - water_target

        # Control law: adjust P_GH to track water usage
        # This is a simple proportional controller
        k_p = 0.01  # Proportional gain
        P_GH_adjustment = -k_p * water_error

        # Rate of change of hydro power
        dP_GH_dt = P_GH_adjustment

        # Rate of change of water used
        dwater_dt = water_rate

        return [dP_GH_dt, dwater_dt]

    def euler_solver(self, f, y0, t_span, n_steps):
        """
        Implement forward Euler method for ODE solving
        """
        t_start, t_end = t_span
        dt = (t_end - t_start) / (n_steps - 1)

        t = np.linspace(t_start, t_end, n_steps)
        y = np.zeros((len(y0), n_steps))
        y[:, 0] = y0

        for i in range(n_steps - 1):
            dy = f(t[i], y[:, i])
            y[:, i+1] = y[:, i] + dt * np.array(dy)

            # Ensure non-negative values
            y[0, i+1] = max(y[0, i+1], 0)  # P_GH >= 0
            y[1, i+1] = max(y[1, i+1], 0)  # water_used >= 0

        return t, y[0], y[1]

    def plot_dynamic_results(self):
        """Plot dynamic simulation results"""
        if self.simulation_data is None:
            return

        self.fig.clear()

        # Create 3x2 subplot grid
        gs = self.fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

        t = self.simulation_data['t']

        # Plot 1: Power Generation vs Time
        ax1 = self.fig.add_subplot(gs[0, 0])
        ax1.plot(t, self.simulation_data['P_GH'], 'b-', linewidth=2, label='Hydro')
        ax1.plot(t, self.simulation_data['P_GT'], 'r-', linewidth=2, label='Thermal')
        ax1.plot(t, self.simulation_data['P_total'], 'g--', linewidth=2, label='Total')
        ax1.set_xlabel('Time (hours)')
        ax1.set_ylabel('Power (MW)')
        ax1.set_title('Power Generation vs Time')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Water Usage vs Time
        ax2 = self.fig.add_subplot(gs[0, 1])
        ax2.plot(t, self.simulation_data['water_used'], 'b-', linewidth=2, label='Water Used')
        ax2.axhline(y=self.params['water_total'], color='r', linestyle='--',
                    linewidth=2, label=f'Target: {self.params["water_total"]:.1f} M m³')
        ax2.fill_between(t, 0, self.simulation_data['water_used'], alpha=0.3)
        ax2.set_xlabel('Time (hours)')
        ax2.set_ylabel('Cumulative Water (Million m³)')
        ax2.set_title('Water Usage vs Time')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Plot 3: Lambda (Incremental Cost) vs Time
        ax3 = self.fig.add_subplot(gs[1, 0])
        ax3.plot(t, self.simulation_data['lambda'], 'g-', linewidth=2)
        ax3.fill_between(t, min(self.simulation_data['lambda'])-1,
                         self.simulation_data['lambda'], alpha=0.3, color='green')
        ax3.set_xlabel('Time (hours)')
        ax3.set_ylabel('Lambda (Rs./MWh)')
        ax3.set_title('Incremental Cost vs Time')
        ax3.grid(True, alpha=0.3)

        # Plot 4: Water Cost vs Time
        ax4 = self.fig.add_subplot(gs[1, 1])
        ax4.plot(t, self.simulation_data['gamma'], 'm-', linewidth=2)
        ax4.fill_between(t, min(self.simulation_data['gamma'])-0.01,
                         self.simulation_data['gamma'], alpha=0.3, color='magenta')
        ax4.set_xlabel('Time (hours)')
        ax4.set_ylabel('Water Cost γ (Rs./hr/m³/s)')
        ax4.set_title('Water Cost vs Time')
        ax4.grid(True, alpha=0.3)

        # Plot 5: Operating Costs vs Time
        ax5 = self.fig.add_subplot(gs[2, 0])
        ax5.plot(t, self.simulation_data['thermal_cost'], 'r-', linewidth=2, label='Thermal')
        ax5.plot(t, self.simulation_data['hydro_cost'], 'b-', linewidth=2, label='Hydro')
        ax5.plot(t, self.simulation_data['total_cost'], 'k--', linewidth=2, label='Total')
        ax5.set_xlabel('Time (hours)')
        ax5.set_ylabel('Cost (Rs./hr)')
        ax5.set_title('Operating Costs vs Time')
        ax5.legend()
        ax5.grid(True, alpha=0.3)

        # Plot 6: Cumulative Cost
        ax6 = self.fig.add_subplot(gs[2, 1])
        cumulative_cost = np.cumsum(self.simulation_data['total_cost']) * (t[1] - t[0])
        ax6.plot(t, cumulative_cost, 'k-', linewidth=2)
        ax6.fill_between(t, 0, cumulative_cost, alpha=0.3, color='gray')
        ax6.set_xlabel('Time (hours)')
        ax6.set_ylabel('Cumulative Cost (Rs.)')
        ax6.set_title('Total Cumulative Cost')
        ax6.grid(True, alpha=0.3)

        # Add final value annotation
        final_cost = cumulative_cost[-1]
        ax6.annotate(f'Final: {final_cost:.2f} Rs.',
                    xy=(t[-1], final_cost),
                    xytext=(t[-1]*0.6, final_cost*0.8),
                    arrowprops=dict(arrowstyle='->', color='red', lw=2),
                    fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

        self.canvas.draw()

    def reset_defaults(self):
        """Reset all parameters to default values"""
        defaults = {
            'thermal_a': 6.0,
            'thermal_b': 12.0,
            'thermal_c': 0.04,
            'hydro_alpha': 28.0,
            'hydro_beta': 0.03,
            'water_total': 450.0,
            'hydro_hours': 16.0,
            'thermal_load': 350.0,
            'time_steps': 100,
        }

        for key, value in defaults.items():
            self.params[key] = value
            if key in self.sliders:
                slider, label = self.sliders[key]
                slider.set(value)
                if key == 'time_steps':
                    label.config(text=f"{int(value)}")
                else:
                    label.config(text=f"{value:.3f}")

        self.calculate_static_solution()


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = HydroThermalSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
