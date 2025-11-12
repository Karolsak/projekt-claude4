"""
Unit Commitment Simulator - Example 4.2
Dynamic simulation with ODE solvers, real-time visualization, and interactive GUI
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.integrate import odeint, solve_ivp
import threading
import time


class UnitCommitmentSimulator:
    """Main application for Unit Commitment dynamic simulation"""

    def __init__(self, root):
        self.root = root
        self.root.title("Unit Commitment Dynamic Simulator - Example 4.2")
        self.root.geometry("1400x900")

        # Unit parameters from Table 4.5
        self.units = [
            {'name': 'Unit 1', 'a': 0.74, 'b': 22.9, 'd': 0, 'min': 1.0, 'max': 14.0},
            {'name': 'Unit 2', 'a': 1.56, 'b': 25.9, 'd': 0, 'min': 1.0, 'max': 14.0},
            {'name': 'Unit 3', 'a': 1.97, 'b': 29.0, 'd': 0, 'min': 1.0, 'max': 14.0},
            {'name': 'Unit 4', 'a': 1.36, 'b': 31.2, 'd': 0, 'min': 1.0, 'max': 14.0}
        ]

        # Simulation parameters
        self.load_demand = tk.DoubleVar(value=8.0)
        self.simulation_speed = tk.DoubleVar(value=1.0)
        self.ode_method = tk.StringVar(value="RK45")
        self.time_step = tk.DoubleVar(value=0.1)

        # Dynamic simulation variables
        self.is_simulating = False
        self.time_data = []
        self.load_data = []
        self.cost_data = []
        self.power_data = {i: [] for i in range(4)}
        self.max_time_points = 500

        # Simulation parameters for load variation
        self.load_amplitude = tk.DoubleVar(value=5.0)
        self.load_frequency = tk.DoubleVar(value=0.5)
        self.load_base = tk.DoubleVar(value=8.0)

        # Unit commitment results
        self.uc_table = {}
        self.F_values = {}

        self.setup_ui()
        self.calculate_uc_table()

        # Configure grid weights for responsive design
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

    def setup_ui(self):
        """Setup the user interface with responsive design"""

        # Main container with grid
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.rowconfigure(1, weight=1)
        main_container.columnconfigure(1, weight=1)

        # ===== Left Panel: Controls =====
        left_panel = ttk.Frame(main_container, padding="5")
        left_panel.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 5))

        # Title
        title_label = ttk.Label(left_panel, text="Unit Commitment Controls",
                                font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 10))

        # Load demand slider
        ttk.Label(left_panel, text="Current Load Demand (MW):").pack(anchor='w')
        load_slider = ttk.Scale(left_panel, from_=1, to=56, orient='horizontal',
                                variable=self.load_demand, command=self.on_load_change)
        load_slider.pack(fill='x', pady=(0, 5))
        self.load_label = ttk.Label(left_panel, text=f"{self.load_demand.get():.2f} MW")
        self.load_label.pack(anchor='w', pady=(0, 10))

        # Dynamic Load Parameters Frame
        load_frame = ttk.LabelFrame(left_panel, text="Dynamic Load Parameters", padding="5")
        load_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(load_frame, text="Base Load (MW):").pack(anchor='w')
        base_slider = ttk.Scale(load_frame, from_=1, to=56, orient='horizontal',
                               variable=self.load_base)
        base_slider.pack(fill='x')

        ttk.Label(load_frame, text="Amplitude (MW):").pack(anchor='w')
        amp_slider = ttk.Scale(load_frame, from_=0, to=10, orient='horizontal',
                              variable=self.load_amplitude)
        amp_slider.pack(fill='x')

        ttk.Label(load_frame, text="Frequency (Hz):").pack(anchor='w')
        freq_slider = ttk.Scale(load_frame, from_=0.1, to=2.0, orient='horizontal',
                               variable=self.load_frequency)
        freq_slider.pack(fill='x')

        # Simulation parameters
        sim_frame = ttk.LabelFrame(left_panel, text="Simulation Parameters", padding="5")
        sim_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(sim_frame, text="Speed:").pack(anchor='w')
        speed_slider = ttk.Scale(sim_frame, from_=0.1, to=5.0, orient='horizontal',
                                variable=self.simulation_speed)
        speed_slider.pack(fill='x')

        ttk.Label(sim_frame, text="Time Step:").pack(anchor='w')
        step_slider = ttk.Scale(sim_frame, from_=0.01, to=0.5, orient='horizontal',
                               variable=self.time_step)
        step_slider.pack(fill='x')

        ttk.Label(sim_frame, text="ODE Method:").pack(anchor='w')
        method_combo = ttk.Combobox(sim_frame, textvariable=self.ode_method,
                                    values=["Euler", "RK45", "RK23", "DOP853"],
                                    state='readonly')
        method_combo.pack(fill='x')

        # Unit parameters adjustment
        unit_frame = ttk.LabelFrame(left_panel, text="Unit 1 Parameters", padding="5")
        unit_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(unit_frame, text="Coefficient a:").pack(anchor='w')
        self.unit1_a = tk.DoubleVar(value=self.units[0]['a'])
        a_slider = ttk.Scale(unit_frame, from_=0.1, to=2.0, orient='horizontal',
                            variable=self.unit1_a, command=self.on_unit_param_change)
        a_slider.pack(fill='x')

        ttk.Label(unit_frame, text="Coefficient b:").pack(anchor='w')
        self.unit1_b = tk.DoubleVar(value=self.units[0]['b'])
        b_slider = ttk.Scale(unit_frame, from_=10, to=40, orient='horizontal',
                            variable=self.unit1_b, command=self.on_unit_param_change)
        b_slider.pack(fill='x')

        # Control buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill='x', pady=(10, 0))

        self.start_btn = ttk.Button(button_frame, text="Start Simulation",
                                    command=self.start_simulation)
        self.start_btn.pack(side='left', expand=True, fill='x', padx=(0, 5))

        self.stop_btn = ttk.Button(button_frame, text="Stop Simulation",
                                   command=self.stop_simulation, state='disabled')
        self.stop_btn.pack(side='left', expand=True, fill='x')

        ttk.Button(left_panel, text="Reset Data", command=self.reset_data).pack(
            fill='x', pady=(5, 0))

        ttk.Button(left_panel, text="Recalculate UC Table",
                  command=self.calculate_uc_table).pack(fill='x', pady=(5, 0))

        # Status display
        status_frame = ttk.LabelFrame(left_panel, text="Current Status", padding="5")
        status_frame.pack(fill='both', expand=True, pady=(10, 0))

        self.status_text = scrolledtext.ScrolledText(status_frame, height=10,
                                                     width=30, wrap=tk.WORD)
        self.status_text.pack(fill='both', expand=True)

        # ===== Top Right: Plots =====
        plot_frame = ttk.Frame(main_container)
        plot_frame.grid(row=0, column=1, sticky="nsew", pady=(0, 5))
        plot_frame.rowconfigure(0, weight=1)
        plot_frame.columnconfigure(0, weight=1)

        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 6), dpi=100)
        self.fig.patch.set_facecolor('#f0f0f0')

        # Create subplots
        self.ax1 = self.fig.add_subplot(2, 2, 1)
        self.ax2 = self.fig.add_subplot(2, 2, 2)
        self.ax3 = self.fig.add_subplot(2, 2, 3)
        self.ax4 = self.fig.add_subplot(2, 2, 4)

        self.fig.tight_layout(pad=3.0)

        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # ===== Bottom Right: UC Table =====
        table_frame = ttk.LabelFrame(main_container, text="Unit Commitment Table",
                                     padding="5")
        table_frame.grid(row=1, column=1, sticky="nsew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.uc_text = scrolledtext.ScrolledText(table_frame, height=15,
                                                 font=('Courier', 9))
        self.uc_text.pack(fill='both', expand=True)

    def cost_function(self, P, unit_idx):
        """Calculate cost for a unit: F = 0.5 * a * P^2 + b * P + d"""
        unit = self.units[unit_idx]
        return 0.5 * unit['a'] * P**2 + unit['b'] * P + unit['d']

    def incremental_cost(self, P, unit_idx):
        """Calculate incremental cost: dC/dP = a * P + b"""
        unit = self.units[unit_idx]
        return unit['a'] * P + unit['b']

    def calculate_unit_costs(self, unit_idx, max_load):
        """Calculate costs for a unit at different load levels"""
        unit = self.units[unit_idx]
        costs = {}

        for load in range(0, int(max_load) + 1):
            if load == 0:
                costs[load] = 0
            elif unit['min'] <= load <= unit['max']:
                costs[load] = self.cost_function(load, unit_idx)
            else:
                costs[load] = float('inf')

        return costs

    def calculate_uc_table(self):
        """Calculate unit commitment table using dynamic programming"""
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, "Calculating UC table...\n\n")

        max_load = int(sum(unit['max'] for unit in self.units))
        n_units = len(self.units)

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

        # Dynamic programming
        # F[n][load] = minimum cost to supply 'load' using first 'n' units
        F = [{} for _ in range(n_units + 1)]
        allocation = [{} for _ in range(n_units + 1)]

        # Base case: no units
        for load in range(max_load + 1):
            F[0][load] = float('inf') if load > 0 else 0
            allocation[0][load] = []

        # Fill DP table
        for n in range(1, n_units + 1):
            for load in range(max_load + 1):
                min_cost = float('inf')
                best_allocation = []

                # Try all possible loads for unit n-1
                for p_unit in range(max(0, load - int(self.units[n-1]['max'])),
                                   load + 1):
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

        self.F_values = F
        self.allocation = allocation

        # Generate UC table display
        self.display_uc_table()

        # Update status
        self.status_text.insert(tk.END, "UC table calculated successfully!\n\n")
        self.update_status()

    def display_uc_table(self):
        """Display the UC table in the text widget"""
        self.uc_text.delete(1.0, tk.END)

        header = "Load (MW) | Cost (Rs/hr) | Unit 1 | Unit 2 | Unit 3 | Unit 4 | Total\n"
        header += "-" * 75 + "\n"
        self.uc_text.insert(tk.END, header)

        n_units = len(self.units)

        # Display for each load level
        for load in range(1, 57):
            cost = self.F_values[n_units].get(load, float('inf'))

            if cost == float('inf'):
                continue

            alloc = self.allocation[n_units].get(load, [])

            # Get power from each unit
            unit_power = [0] * n_units
            for unit_idx, power in alloc:
                unit_power[unit_idx] = power

            # Determine status (1 = on, 0 = off)
            status = ['1' if p > 0 else '0' for p in unit_power]

            total_power = sum(unit_power)

            line = f"{load:5.0f}     | {cost:10.2f}   | "
            line += " | ".join([f"{p:5.2f}" for p in unit_power])
            line += f" | {total_power:5.2f}\n"

            self.uc_text.insert(tk.END, line)

        # Add summary table
        self.uc_text.insert(tk.END, "\n" + "="*75 + "\n")
        self.uc_text.insert(tk.END, "UNIT COMMITMENT STATUS TABLE\n")
        self.uc_text.insert(tk.END, "="*75 + "\n")
        self.uc_text.insert(tk.END, "Load Range | Unit 1 | Unit 2 | Unit 3 | Unit 4\n")
        self.uc_text.insert(tk.END, "-" * 75 + "\n")

        # Simplified status ranges
        ranges = [
            ("1-5", [1, 0, 0, 0]),
            ("6-13", [1, 1, 0, 0]),
            ("14-18", [1, 1, 1, 0]),
            ("19-56", [1, 1, 1, 1])
        ]

        for load_range, status in ranges:
            status_str = " | ".join([f"  {s}   " for s in status])
            self.uc_text.insert(tk.END, f"{load_range:10s} | {status_str}\n")

    def economic_dispatch(self, load, committed_units):
        """Perform economic dispatch using lambda iteration"""
        if not committed_units:
            return {}, 0, 0

        # Lambda iteration method
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
                # P = (lambda - b) / a
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

        # Calculate total cost
        total_cost = sum(self.cost_function(power_allocation[i], i)
                        for i in committed_units)

        return power_allocation, total_cost, lambda_mid

    def dynamic_load_function(self, t):
        """Dynamic load variation function"""
        base = self.load_base.get()
        amp = self.load_amplitude.get()
        freq = self.load_frequency.get()

        # Sinusoidal variation
        load = base + amp * np.sin(2 * np.pi * freq * t)

        # Ensure within bounds
        return max(1.0, min(56.0, load))

    def system_dynamics(self, t, y):
        """
        System dynamics for ODE solver
        y = [P1, P2, P3, P4, load]
        dy/dt = rate of change
        """
        P = y[:4]
        current_load = self.dynamic_load_function(t)

        # Get optimal allocation for current load
        n_units = len(self.units)
        alloc = self.allocation[n_units].get(int(current_load), [])

        target_power = [0] * 4
        for unit_idx, power in alloc:
            target_power[unit_idx] = power

        # First-order dynamics: rate of change proportional to error
        tau = 1.0  # Time constant
        dP = [(target_power[i] - P[i]) / tau for i in range(4)]

        return dP + [0]  # Load change handled separately

    def euler_step(self, t, y, dt):
        """Euler method integration step"""
        dy = self.system_dynamics(t, y)
        return [y[i] + dt * dy[i] for i in range(len(y))]

    def simulate_step(self, t):
        """Perform one simulation step"""
        # Get current load
        current_load = self.dynamic_load_function(t)

        # Get optimal unit commitment
        n_units = len(self.units)
        alloc = self.allocation[n_units].get(int(current_load), [])

        # Get committed units
        committed_units = [idx for idx, _ in alloc]

        # Perform economic dispatch
        power_alloc, total_cost, lambda_val = self.economic_dispatch(
            current_load, committed_units)

        # Store data
        self.time_data.append(t)
        self.load_data.append(current_load)
        self.cost_data.append(total_cost)

        for i in range(4):
            self.power_data[i].append(power_alloc.get(i, 0))

        # Limit data points
        if len(self.time_data) > self.max_time_points:
            self.time_data.pop(0)
            self.load_data.pop(0)
            self.cost_data.pop(0)
            for i in range(4):
                self.power_data[i].pop(0)

        return power_alloc, total_cost, lambda_val

    def update_plots(self):
        """Update all plots"""
        if len(self.time_data) < 2:
            return

        # Clear all axes
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.clear()

        # Plot 1: Load demand over time
        self.ax1.plot(self.time_data, self.load_data, 'b-', linewidth=2)
        self.ax1.set_xlabel('Time (s)')
        self.ax1.set_ylabel('Load (MW)')
        self.ax1.set_title('Load Demand vs Time')
        self.ax1.grid(True, alpha=0.3)

        # Plot 2: Total cost over time
        self.ax2.plot(self.time_data, self.cost_data, 'r-', linewidth=2)
        self.ax2.set_xlabel('Time (s)')
        self.ax2.set_ylabel('Cost (Rs/hr)')
        self.ax2.set_title('Total Generation Cost vs Time')
        self.ax2.grid(True, alpha=0.3)

        # Plot 3: Unit power outputs
        colors = ['blue', 'green', 'red', 'orange']
        for i in range(4):
            self.ax3.plot(self.time_data, self.power_data[i],
                         color=colors[i], linewidth=2, label=f'Unit {i+1}')
        self.ax3.set_xlabel('Time (s)')
        self.ax3.set_ylabel('Power (MW)')
        self.ax3.set_title('Unit Power Outputs vs Time')
        self.ax3.legend(loc='upper right', fontsize=8)
        self.ax3.grid(True, alpha=0.3)

        # Plot 4: Cost vs Load (current point highlighted)
        if len(self.load_data) > 0 and len(self.cost_data) > 0:
            # Plot historical points
            self.ax4.scatter(self.load_data[:-1], self.cost_data[:-1],
                           c='lightblue', s=10, alpha=0.5)
            # Highlight current point
            self.ax4.scatter([self.load_data[-1]], [self.cost_data[-1]],
                           c='red', s=100, marker='*', zorder=5,
                           label='Current')
            self.ax4.set_xlabel('Load (MW)')
            self.ax4.set_ylabel('Cost (Rs/hr)')
            self.ax4.set_title('Cost vs Load Characteristic')
            self.ax4.legend()
            self.ax4.grid(True, alpha=0.3)

        self.fig.tight_layout(pad=2.0)
        self.canvas.draw()

    def simulation_loop(self):
        """Main simulation loop running in separate thread"""
        t = 0

        while self.is_simulating:
            # Perform simulation step
            power_alloc, total_cost, lambda_val = self.simulate_step(t)

            # Update plots (on main thread)
            self.root.after(0, self.update_plots)

            # Update status display
            status_msg = f"Time: {t:.2f}s\n"
            status_msg += f"Load: {self.load_data[-1]:.2f} MW\n"
            status_msg += f"Cost: {total_cost:.2f} Rs/hr\n"
            status_msg += f"Lambda: {lambda_val:.2f} Rs/MWh\n\n"
            status_msg += "Unit Powers (MW):\n"
            for i in range(4):
                status_msg += f"  Unit {i+1}: {power_alloc.get(i, 0):.2f}\n"

            self.root.after(0, lambda: self.update_status_text(status_msg))

            # Time step with speed control
            dt = self.time_step.get()
            t += dt

            # Sleep based on simulation speed
            time.sleep(dt / self.simulation_speed.get())

    def update_status_text(self, msg):
        """Update status text widget"""
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, msg)

    def start_simulation(self):
        """Start dynamic simulation"""
        if not self.is_simulating:
            self.is_simulating = True
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')

            # Start simulation in separate thread
            sim_thread = threading.Thread(target=self.simulation_loop, daemon=True)
            sim_thread.start()

    def stop_simulation(self):
        """Stop dynamic simulation"""
        self.is_simulating = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')

    def reset_data(self):
        """Reset all simulation data"""
        self.stop_simulation()
        self.time_data = []
        self.load_data = []
        self.cost_data = []
        self.power_data = {i: [] for i in range(4)}

        # Clear plots
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.clear()
        self.canvas.draw()

        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, "Data reset. Ready for new simulation.\n")

    def on_load_change(self, *args):
        """Handle load slider change"""
        load = self.load_demand.get()
        self.load_label.config(text=f"{load:.2f} MW")
        self.update_status()

    def on_unit_param_change(self, *args):
        """Handle unit parameter change"""
        self.units[0]['a'] = self.unit1_a.get()
        self.units[0]['b'] = self.unit1_b.get()
        # Recalculate UC table with new parameters
        self.calculate_uc_table()

    def update_status(self):
        """Update status display with current load information"""
        load = int(self.load_demand.get())
        n_units = len(self.units)

        if load in self.F_values[n_units]:
            cost = self.F_values[n_units][load]
            alloc = self.allocation[n_units].get(load, [])

            msg = f"Load: {load} MW\n"
            msg += f"Minimum Cost: {cost:.2f} Rs/hr\n\n"
            msg += "Committed Units:\n"

            for unit_idx, power in alloc:
                msg += f"  Unit {unit_idx + 1}: {power:.2f} MW\n"

            # Perform economic dispatch
            committed = [idx for idx, _ in alloc]
            if committed:
                power_alloc, total_cost, lambda_val = self.economic_dispatch(
                    load, committed)

                msg += f"\nOptimal Economic Dispatch:\n"
                msg += f"Lambda: {lambda_val:.2f} Rs/MWh\n"
                for unit_idx, power in power_alloc.items():
                    msg += f"  Unit {unit_idx + 1}: {power:.2f} MW\n"

            if not self.is_simulating:
                self.status_text.delete(1.0, tk.END)
                self.status_text.insert(tk.END, msg)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = UnitCommitmentSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
