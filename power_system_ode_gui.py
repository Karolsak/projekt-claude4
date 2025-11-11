#!/usr/bin/env python3
"""
Power System Economic Dispatch Simulator with ODE Solver
Example 3.10: Economic Load Dispatch with Dynamic Simulation

Features:
- Real-time ODE solver (RK45 and Euler methods)
- Dynamic visualization with matplotlib
- Responsive window resizing
- Interactive sliders for parameters
- Economic dispatch optimization
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from datetime import datetime, timedelta


class PowerSystemSimulator:
    """Power system economic dispatch simulator with ODE solver"""

    def __init__(self):
        # Cost function coefficients for Unit 1: C1 = a1*P1^2 + b1*P1 + c1
        self.a1 = 0.024
        self.b1 = 8.0
        self.c1 = 80e6  # 80 * 10^6

        # Cost function coefficients for Unit 2: C2 = a2*P2^2 + b2*P2 + c2
        self.a2 = 0.04
        self.b2 = 6.0
        self.c2 = 120e6  # 120 * 10^6

        # Unit limits (MW)
        self.P_min = 10.0
        self.P_max = 100.0

        # Ramping rates (MW/s) for dynamic simulation
        self.ramp_rate_1 = 10.0  # MW/s
        self.ramp_rate_2 = 10.0  # MW/s

        # Fuel cost (Rs. per million Btu)
        self.fuel_cost = 2.0

        # Simulation parameters
        self.dt = 0.1  # Time step (seconds)
        self.time_scale = 1.0  # Time scaling factor for visualization

        # State variables
        self.P1 = 25.0  # Current power output Unit 1 (MW)
        self.P2 = 25.0  # Current power output Unit 2 (MW)
        self.t = 0.0  # Current simulation time (hours)

        # History arrays for plotting
        self.max_history = 1000
        self.time_history = []
        self.P1_history = []
        self.P2_history = []
        self.load_history = []
        self.cost_history = []
        self.lambda_history = []

    def incremental_cost(self, P, unit=1):
        """Calculate incremental cost dC/dP for a unit"""
        if unit == 1:
            return 2 * self.a1 * P + self.b1
        else:
            return 2 * self.a2 * P + self.b2

    def cost(self, P, unit=1):
        """Calculate total cost for a unit"""
        if unit == 1:
            return self.a1 * P**2 + self.b1 * P + self.c1
        else:
            return self.a2 * P**2 + self.b2 * P + self.c2

    def get_load_at_time(self, t_hours):
        """Get load demand at given time (hours)
        50 MW from 6 AM to 6 PM (6-18 hours)
        150 MW from 6 PM to 6 AM (18-24 and 0-6 hours)
        """
        t_mod = t_hours % 24  # Get hour of day (0-24)
        if 6 <= t_mod < 18:
            return 50.0
        else:
            return 150.0

    def economic_dispatch(self, load):
        """
        Solve economic dispatch problem for given load
        Returns optimal P1, P2, and lambda (incremental cost)

        Condition: dC1/dP1 = dC2/dP2 = lambda
        Constraint: P1 + P2 = Load

        From equal incremental costs:
        2*a1*P1 + b1 = 2*a2*P2 + b2
        """
        # Check if load is within feasible range
        if load < 2 * self.P_min or load > 2 * self.P_max:
            # Adjust to feasible range
            load = max(2 * self.P_min, min(load, 2 * self.P_max))

        # From equal incremental cost condition:
        # 2*a1*P1 + b1 = 2*a2*P2 + b2
        # 2*a1*P1 - 2*a2*P2 = b2 - b1
        # And P1 + P2 = Load

        # Solving: P1 + P2 = Load and 2*a1*P1 - 2*a2*P2 = b2 - b1
        # P2 = Load - P1
        # 2*a1*P1 - 2*a2*(Load - P1) = b2 - b1
        # 2*a1*P1 - 2*a2*Load + 2*a2*P1 = b2 - b1
        # P1*(2*a1 + 2*a2) = b2 - b1 + 2*a2*Load

        P1_optimal = (self.b2 - self.b1 + 2*self.a2*load) / (2*(self.a1 + self.a2))
        P2_optimal = load - P1_optimal

        # Apply unit limits
        P1_optimal = max(self.P_min, min(P1_optimal, self.P_max))
        P2_optimal = max(self.P_min, min(P2_optimal, self.P_max))

        # Adjust if sum doesn't match load due to limits
        total = P1_optimal + P2_optimal
        if total != load:
            if total < load:
                # Increase both proportionally
                deficit = load - total
                if P1_optimal < self.P_max:
                    increase1 = min(self.P_max - P1_optimal, deficit/2)
                    P1_optimal += increase1
                    deficit -= increase1
                if P2_optimal < self.P_max and deficit > 0:
                    increase2 = min(self.P_max - P2_optimal, deficit)
                    P2_optimal += increase2
            else:
                # Decrease both proportionally
                excess = total - load
                if P1_optimal > self.P_min:
                    decrease1 = min(P1_optimal - self.P_min, excess/2)
                    P1_optimal -= decrease1
                    excess -= decrease1
                if P2_optimal > self.P_min and excess > 0:
                    decrease2 = min(P2_optimal - self.P_min, excess)
                    P2_optimal -= decrease2

        # Calculate lambda (incremental cost at optimal point)
        lambda_val = self.incremental_cost(P1_optimal, unit=1)

        return P1_optimal, P2_optimal, lambda_val

    def ode_system(self, state, t, load):
        """
        ODE system for power generation dynamics
        Models first-order ramping dynamics

        dP1/dt = (P1_target - P1) / tau1
        dP2/dt = (P2_target - P2) / tau2
        """
        P1, P2 = state

        # Get optimal dispatch for current load
        P1_target, P2_target, _ = self.economic_dispatch(load)

        # Time constants (seconds) - related to ramping rates
        tau1 = 5.0  # Time constant for Unit 1
        tau2 = 5.0  # Time constant for Unit 2

        # Calculate derivatives with ramping rate limits
        dP1_dt = (P1_target - P1) / tau1
        dP2_dt = (P2_target - P2) / tau2

        # Apply ramping rate limits
        dP1_dt = np.clip(dP1_dt, -self.ramp_rate_1, self.ramp_rate_1)
        dP2_dt = np.clip(dP2_dt, -self.ramp_rate_2, self.ramp_rate_2)

        return [dP1_dt, dP2_dt]

    def euler_step(self, load):
        """Euler method for ODE integration"""
        state = [self.P1, self.P2]
        derivatives = self.ode_system(state, self.t, load)

        self.P1 += derivatives[0] * self.dt
        self.P2 += derivatives[1] * self.dt

        # Apply limits
        self.P1 = max(self.P_min, min(self.P1, self.P_max))
        self.P2 = max(self.P_min, min(self.P2, self.P_max))

    def rk45_step(self, load):
        """RK45 (Runge-Kutta 4th order) method for ODE integration"""
        state = [self.P1, self.P2]

        # RK4 coefficients
        k1 = self.ode_system(state, self.t, load)

        state2 = [state[0] + 0.5*self.dt*k1[0], state[1] + 0.5*self.dt*k1[1]]
        k2 = self.ode_system(state2, self.t + 0.5*self.dt, load)

        state3 = [state[0] + 0.5*self.dt*k2[0], state[1] + 0.5*self.dt*k2[1]]
        k3 = self.ode_system(state3, self.t + 0.5*self.dt, load)

        state4 = [state[0] + self.dt*k3[0], state[1] + self.dt*k3[1]]
        k4 = self.ode_system(state4, self.t + self.dt, load)

        # Update state
        self.P1 += (self.dt / 6.0) * (k1[0] + 2*k2[0] + 2*k3[0] + k4[0])
        self.P2 += (self.dt / 6.0) * (k1[1] + 2*k2[1] + 2*k3[1] + k4[1])

        # Apply limits
        self.P1 = max(self.P_min, min(self.P1, self.P_max))
        self.P2 = max(self.P_min, min(self.P2, self.P_max))

    def step(self, method='rk45'):
        """Advance simulation by one time step"""
        # Get current load
        load = self.get_load_at_time(self.t)

        # Integrate using selected method
        if method.lower() == 'euler':
            self.euler_step(load)
        else:
            self.rk45_step(load)

        # Update time (convert dt from seconds to hours)
        self.t += self.dt / 3600.0 * self.time_scale

        # Calculate costs
        C1 = self.cost(self.P1, unit=1) * self.fuel_cost / 1e6  # Rs./hr
        C2 = self.cost(self.P2, unit=2) * self.fuel_cost / 1e6  # Rs./hr
        total_cost = C1 + C2

        # Calculate lambda
        lambda_val = self.incremental_cost(self.P1, unit=1)

        # Store history
        self.time_history.append(self.t)
        self.P1_history.append(self.P1)
        self.P2_history.append(self.P2)
        self.load_history.append(load)
        self.cost_history.append(total_cost)
        self.lambda_history.append(lambda_val)

        # Limit history size
        if len(self.time_history) > self.max_history:
            self.time_history.pop(0)
            self.P1_history.pop(0)
            self.P2_history.pop(0)
            self.load_history.pop(0)
            self.cost_history.pop(0)
            self.lambda_history.pop(0)

    def reset(self):
        """Reset simulation"""
        self.P1 = 25.0
        self.P2 = 25.0
        self.t = 0.0
        self.time_history = []
        self.P1_history = []
        self.P2_history = []
        self.load_history = []
        self.cost_history = []
        self.lambda_history = []


class PowerSystemGUI:
    """Tkinter GUI for Power System Simulator"""

    def __init__(self, root):
        self.root = root
        self.root.title("Power System Economic Dispatch - ODE Solver Simulator")
        self.root.geometry("1400x900")

        # Create simulator
        self.simulator = PowerSystemSimulator()

        # Simulation control
        self.running = False
        self.method = 'rk45'
        self.update_interval = 50  # milliseconds

        # Create UI
        self.create_ui()

        # Start animation
        self.animate()

        # Bind resize event
        self.root.bind('<Configure>', self.on_resize)

    def create_ui(self):
        """Create user interface"""
        # Main container with grid layout
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configure grid weights for responsive design
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)

        # Left panel for controls
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding=10)
        control_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Right panel for plots
        plot_frame = ttk.Frame(main_frame)
        plot_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

        # Create controls
        self.create_controls(control_frame)

        # Create plots
        self.create_plots(plot_frame)

    def create_controls(self, parent):
        """Create control widgets"""
        row = 0

        # Simulation control buttons
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10, sticky='ew')

        self.start_button = ttk.Button(button_frame, text="▶ Start", command=self.start_simulation)
        self.start_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.stop_button = ttk.Button(button_frame, text="⏸ Pause", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.reset_button = ttk.Button(button_frame, text="↻ Reset", command=self.reset_simulation)
        self.reset_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        row += 1

        # ODE Method selection
        ttk.Label(parent, text="ODE Solver Method:", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=(15,5), sticky='w')
        row += 1

        self.method_var = tk.StringVar(value='rk45')
        methods = [('RK45 (Runge-Kutta)', 'rk45'), ('Euler Method', 'euler')]
        for text, value in methods:
            ttk.Radiobutton(parent, text=text, variable=self.method_var, value=value,
                          command=self.update_method).grid(row=row, column=0, columnspan=2, sticky='w')
            row += 1

        # Time scale slider
        ttk.Label(parent, text="Time Scale:", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=(15,5), sticky='w')
        row += 1

        self.time_scale_var = tk.DoubleVar(value=1.0)
        time_scale_slider = ttk.Scale(parent, from_=0.1, to=10.0, variable=self.time_scale_var,
                                     orient=tk.HORIZONTAL, command=self.update_time_scale)
        time_scale_slider.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1

        self.time_scale_label = ttk.Label(parent, text="1.0x")
        self.time_scale_label.grid(row=row, column=0, columnspan=2, pady=5)
        row += 1

        # Unit 1 parameters
        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky='ew', pady=15)
        row += 1

        ttk.Label(parent, text="Unit 1 Parameters:", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=5, sticky='w')
        row += 1

        # a1 coefficient
        ttk.Label(parent, text="a₁ (cost coef.):").grid(row=row, column=0, sticky='w', pady=5)
        self.a1_var = tk.DoubleVar(value=self.simulator.a1)
        a1_slider = ttk.Scale(parent, from_=0.01, to=0.1, variable=self.a1_var,
                            orient=tk.HORIZONTAL, command=self.update_a1)
        a1_slider.grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        self.a1_label = ttk.Label(parent, text=f"{self.simulator.a1:.4f}")
        self.a1_label.grid(row=row, column=0, columnspan=2)
        row += 1

        # b1 coefficient
        ttk.Label(parent, text="b₁ (cost coef.):").grid(row=row, column=0, sticky='w', pady=5)
        self.b1_var = tk.DoubleVar(value=self.simulator.b1)
        b1_slider = ttk.Scale(parent, from_=1.0, to=20.0, variable=self.b1_var,
                            orient=tk.HORIZONTAL, command=self.update_b1)
        b1_slider.grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        self.b1_label = ttk.Label(parent, text=f"{self.simulator.b1:.2f}")
        self.b1_label.grid(row=row, column=0, columnspan=2)
        row += 1

        # Ramp rate 1
        ttk.Label(parent, text="Ramp Rate 1 (MW/s):").grid(row=row, column=0, sticky='w', pady=5)
        self.ramp1_var = tk.DoubleVar(value=self.simulator.ramp_rate_1)
        ramp1_slider = ttk.Scale(parent, from_=1.0, to=50.0, variable=self.ramp1_var,
                               orient=tk.HORIZONTAL, command=self.update_ramp1)
        ramp1_slider.grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        self.ramp1_label = ttk.Label(parent, text=f"{self.simulator.ramp_rate_1:.1f}")
        self.ramp1_label.grid(row=row, column=0, columnspan=2)
        row += 1

        # Unit 2 parameters
        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky='ew', pady=15)
        row += 1

        ttk.Label(parent, text="Unit 2 Parameters:", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=5, sticky='w')
        row += 1

        # a2 coefficient
        ttk.Label(parent, text="a₂ (cost coef.):").grid(row=row, column=0, sticky='w', pady=5)
        self.a2_var = tk.DoubleVar(value=self.simulator.a2)
        a2_slider = ttk.Scale(parent, from_=0.01, to=0.1, variable=self.a2_var,
                            orient=tk.HORIZONTAL, command=self.update_a2)
        a2_slider.grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        self.a2_label = ttk.Label(parent, text=f"{self.simulator.a2:.4f}")
        self.a2_label.grid(row=row, column=0, columnspan=2)
        row += 1

        # b2 coefficient
        ttk.Label(parent, text="b₂ (cost coef.):").grid(row=row, column=0, sticky='w', pady=5)
        self.b2_var = tk.DoubleVar(value=self.simulator.b2)
        b2_slider = ttk.Scale(parent, from_=1.0, to=20.0, variable=self.b2_var,
                            orient=tk.HORIZONTAL, command=self.update_b2)
        b2_slider.grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        self.b2_label = ttk.Label(parent, text=f"{self.simulator.b2:.2f}")
        self.b2_label.grid(row=row, column=0, columnspan=2)
        row += 1

        # Ramp rate 2
        ttk.Label(parent, text="Ramp Rate 2 (MW/s):").grid(row=row, column=0, sticky='w', pady=5)
        self.ramp2_var = tk.DoubleVar(value=self.simulator.ramp_rate_2)
        ramp2_slider = ttk.Scale(parent, from_=1.0, to=50.0, variable=self.ramp2_var,
                               orient=tk.HORIZONTAL, command=self.update_ramp2)
        ramp2_slider.grid(row=row, column=1, sticky='ew', pady=5)
        row += 1
        self.ramp2_label = ttk.Label(parent, text=f"{self.simulator.ramp_rate_2:.1f}")
        self.ramp2_label.grid(row=row, column=0, columnspan=2)
        row += 1

        # Status display
        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky='ew', pady=15)
        row += 1

        ttk.Label(parent, text="Status:", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=5, sticky='w')
        row += 1

        self.status_text = tk.Text(parent, height=8, width=30, wrap=tk.WORD, font=('Courier', 9))
        self.status_text.grid(row=row, column=0, columnspan=2, sticky='nsew', pady=5)

        # Make parent expandable
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(1, weight=1)

    def create_plots(self, parent):
        """Create matplotlib plots"""
        # Create figure with subplots
        self.fig = Figure(figsize=(12, 8), facecolor='white')

        # Create subplots (2x2 grid)
        self.ax1 = self.fig.add_subplot(2, 2, 1)
        self.ax2 = self.fig.add_subplot(2, 2, 2)
        self.ax3 = self.fig.add_subplot(2, 2, 3)
        self.ax4 = self.fig.add_subplot(2, 2, 4)

        self.fig.tight_layout(pad=3.0)

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initial plot setup
        self.setup_plots()

    def setup_plots(self):
        """Setup initial plot configurations"""
        # Plot 1: Power Generation
        self.ax1.clear()
        self.ax1.set_title('Power Generation (MW)', fontsize=10, fontweight='bold')
        self.ax1.set_xlabel('Time (hours)', fontsize=9)
        self.ax1.set_ylabel('Power (MW)', fontsize=9)
        self.ax1.grid(True, alpha=0.3)
        self.ax1.legend(['Unit 1', 'Unit 2', 'Load'], loc='upper right', fontsize=8)

        # Plot 2: Total Cost
        self.ax2.clear()
        self.ax2.set_title('Total Generation Cost (Rs./hr)', fontsize=10, fontweight='bold')
        self.ax2.set_xlabel('Time (hours)', fontsize=9)
        self.ax2.set_ylabel('Cost (Rs./hr)', fontsize=9)
        self.ax2.grid(True, alpha=0.3)

        # Plot 3: Incremental Cost (Lambda)
        self.ax3.clear()
        self.ax3.set_title('Incremental Cost λ (Rs./MWh)', fontsize=10, fontweight='bold')
        self.ax3.set_xlabel('Time (hours)', fontsize=9)
        self.ax3.set_ylabel('λ (Rs./MWh)', fontsize=9)
        self.ax3.grid(True, alpha=0.3)

        # Plot 4: Power Distribution Pie Chart (current snapshot)
        self.ax4.clear()
        self.ax4.set_title('Current Power Distribution', fontsize=10, fontweight='bold')

    def update_plots(self):
        """Update all plots with current data"""
        if len(self.simulator.time_history) == 0:
            return

        times = np.array(self.simulator.time_history)
        P1 = np.array(self.simulator.P1_history)
        P2 = np.array(self.simulator.P2_history)
        load = np.array(self.simulator.load_history)
        cost = np.array(self.simulator.cost_history)
        lambda_vals = np.array(self.simulator.lambda_history)

        # Plot 1: Power Generation
        self.ax1.clear()
        self.ax1.plot(times, P1, 'b-', linewidth=2, label='Unit 1')
        self.ax1.plot(times, P2, 'r-', linewidth=2, label='Unit 2')
        self.ax1.plot(times, load, 'g--', linewidth=2, label='Load', alpha=0.7)
        self.ax1.fill_between(times, 0, P1, alpha=0.3, color='blue')
        self.ax1.fill_between(times, P1, P1+P2, alpha=0.3, color='red')
        self.ax1.set_title('Power Generation (MW)', fontsize=10, fontweight='bold')
        self.ax1.set_xlabel('Time (hours)', fontsize=9)
        self.ax1.set_ylabel('Power (MW)', fontsize=9)
        self.ax1.grid(True, alpha=0.3)
        self.ax1.legend(loc='upper right', fontsize=8)
        self.ax1.set_ylim([0, 200])

        # Plot 2: Total Cost
        self.ax2.clear()
        self.ax2.plot(times, cost, 'purple', linewidth=2)
        self.ax2.fill_between(times, 0, cost, alpha=0.3, color='purple')
        self.ax2.set_title('Total Generation Cost (Rs./hr)', fontsize=10, fontweight='bold')
        self.ax2.set_xlabel('Time (hours)', fontsize=9)
        self.ax2.set_ylabel('Cost (Rs./hr)', fontsize=9)
        self.ax2.grid(True, alpha=0.3)

        # Plot 3: Incremental Cost (Lambda)
        self.ax3.clear()
        self.ax3.plot(times, lambda_vals, 'orange', linewidth=2)
        self.ax3.fill_between(times, min(lambda_vals)*0.9, lambda_vals, alpha=0.3, color='orange')
        self.ax3.set_title('Incremental Cost λ (Rs./MWh)', fontsize=10, fontweight='bold')
        self.ax3.set_xlabel('Time (hours)', fontsize=9)
        self.ax3.set_ylabel('λ (Rs./MWh)', fontsize=9)
        self.ax3.grid(True, alpha=0.3)

        # Plot 4: Current Power Distribution (Pie Chart)
        self.ax4.clear()
        current_P1 = P1[-1]
        current_P2 = P2[-1]
        total_power = current_P1 + current_P2

        if total_power > 0:
            sizes = [current_P1, current_P2]
            labels = [f'Unit 1\n{current_P1:.1f} MW\n({current_P1/total_power*100:.1f}%)',
                     f'Unit 2\n{current_P2:.1f} MW\n({current_P2/total_power*100:.1f}%)']
            colors = ['#3498db', '#e74c3c']
            explode = (0.05, 0.05)

            self.ax4.pie(sizes, explode=explode, labels=labels, colors=colors,
                        autopct='', shadow=True, startangle=90)
            self.ax4.set_title(f'Current Power Distribution\nTotal: {total_power:.1f} MW',
                             fontsize=10, fontweight='bold')

        self.fig.tight_layout(pad=3.0)
        self.canvas.draw()

    def update_status(self):
        """Update status text display"""
        self.status_text.delete(1.0, tk.END)

        if len(self.simulator.time_history) > 0:
            current_time = self.simulator.t
            current_load = self.simulator.load_history[-1]
            current_P1 = self.simulator.P1
            current_P2 = self.simulator.P2
            current_cost = self.simulator.cost_history[-1]
            current_lambda = self.simulator.lambda_history[-1]

            # Format time as HH:MM
            hours = int(current_time % 24)
            minutes = int((current_time % 1) * 60)
            time_str = f"{hours:02d}:{minutes:02d}"

            status = f"""Time: {time_str} ({current_time:.2f} hrs)
Method: {self.method.upper()}

Load Demand: {current_load:.1f} MW

Unit 1: {current_P1:.2f} MW
Unit 2: {current_P2:.2f} MW
Total: {current_P1+current_P2:.2f} MW

Total Cost: {current_cost:.2f} Rs/hr
Lambda (λ): {current_lambda:.2f} Rs/MWh

IC₁: {self.simulator.incremental_cost(current_P1, 1):.2f}
IC₂: {self.simulator.incremental_cost(current_P2, 2):.2f}
"""
            self.status_text.insert(1.0, status)

    def animate(self):
        """Animation loop"""
        if self.running:
            # Perform simulation step
            self.simulator.step(method=self.method)

            # Update plots and status
            self.update_plots()
            self.update_status()

        # Schedule next update
        self.root.after(self.update_interval, self.animate)

    def start_simulation(self):
        """Start simulation"""
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_simulation(self):
        """Stop simulation"""
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def reset_simulation(self):
        """Reset simulation"""
        self.running = False
        self.simulator.reset()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.setup_plots()
        self.update_status()
        self.canvas.draw()

    def update_method(self):
        """Update ODE solver method"""
        self.method = self.method_var.get()

    def update_time_scale(self, value):
        """Update time scale"""
        self.simulator.time_scale = self.time_scale_var.get()
        self.time_scale_label.config(text=f"{self.simulator.time_scale:.1f}x")

    def update_a1(self, value):
        """Update a1 coefficient"""
        self.simulator.a1 = self.a1_var.get()
        self.a1_label.config(text=f"{self.simulator.a1:.4f}")

    def update_b1(self, value):
        """Update b1 coefficient"""
        self.simulator.b1 = self.b1_var.get()
        self.b1_label.config(text=f"{self.simulator.b1:.2f}")

    def update_ramp1(self, value):
        """Update ramp rate 1"""
        self.simulator.ramp_rate_1 = self.ramp1_var.get()
        self.ramp1_label.config(text=f"{self.simulator.ramp_rate_1:.1f}")

    def update_a2(self, value):
        """Update a2 coefficient"""
        self.simulator.a2 = self.a2_var.get()
        self.a2_label.config(text=f"{self.simulator.a2:.4f}")

    def update_b2(self, value):
        """Update b2 coefficient"""
        self.simulator.b2 = self.b2_var.get()
        self.b2_label.config(text=f"{self.simulator.b2:.2f}")

    def update_ramp2(self, value):
        """Update ramp rate 2"""
        self.simulator.ramp_rate_2 = self.ramp2_var.get()
        self.ramp2_label.config(text=f"{self.simulator.ramp_rate_2:.1f}")

    def on_resize(self, event):
        """Handle window resize event"""
        # The canvas will automatically adjust due to pack with expand=True
        pass


def main():
    """Main entry point"""
    root = tk.Tk()
    app = PowerSystemGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
