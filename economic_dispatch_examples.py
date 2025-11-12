#!/usr/bin/env python3
"""
Power System Economic Dispatch Simulator
Examples 3.18 and 3.19: Penalty Factors and Economic Operation

Features:
- Real-time ODE solver (RK45 and Euler methods)
- Dynamic visualization with matplotlib
- Responsive window resizing
- Interactive sliders for all parameters
- Automatic width/height adjustment
- Results visualization with dynamic graphs
- Tabbed interface for multiple examples
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.integrate import odeint


class Example318Simulator:
    """Example 3.18: Penalty Factor Calculation"""

    def __init__(self):
        # System parameters
        self.lambda_sys = 60.0  # System lambda (Rs./MWh)
        self.delta_PG2 = 100.0  # Change in Plant-2 output (kW)
        self.delta_PL = 12.0    # Change in losses (kW)

        # Dynamic simulation parameters
        self.time = 0.0
        self.dt = 0.01

        # State variables for ODE simulation
        self.PG2 = 100.0  # Initial Plant-2 output (MW)
        self.losses = 10.0  # Initial losses (MW)

        # History for plotting
        self.max_history = 500
        self.time_history = []
        self.PG2_history = []
        self.losses_history = []
        self.L2_history = []
        self.incremental_cost_history = []
        self.additional_cost_history = []

    def calculate_penalty_factor(self):
        """Calculate penalty factor L2"""
        dPL_dPG2 = self.delta_PL / self.delta_PG2
        L2 = 1.0 / (1.0 - dPL_dPG2)
        return L2, dPL_dPG2

    def calculate_incremental_cost(self):
        """Calculate incremental cost at Plant-2"""
        L2, _ = self.calculate_penalty_factor()
        dC2_dPG2 = self.lambda_sys / L2
        return dC2_dPG2

    def calculate_additional_cost(self, delta_MW=1.0):
        """Calculate additional cost for increasing output"""
        dC2_dPG2 = self.calculate_incremental_cost()
        additional_cost = dC2_dPG2 * delta_MW
        return additional_cost

    def ode_system(self, state, t, target_PG2):
        """ODE system for dynamic simulation"""
        PG2, losses = state

        # Simple dynamics: power and losses approach targets
        tau_power = 2.0  # Time constant for power changes
        tau_losses = 1.0  # Time constant for losses

        # Target losses based on power change
        dPL_dPG2 = self.delta_PL / self.delta_PG2
        target_losses = self.losses + dPL_dPG2 * (target_PG2 - self.PG2)

        # Derivatives
        dPG2_dt = (target_PG2 - PG2) / tau_power
        dlosses_dt = (target_losses - losses) / tau_losses

        return [dPG2_dt, dlosses_dt]

    def euler_step(self, target_PG2):
        """Euler method step"""
        state = [self.PG2, self.losses]
        derivatives = self.ode_system(state, self.time, target_PG2)

        self.PG2 += derivatives[0] * self.dt
        self.losses += derivatives[1] * self.dt
        self.time += self.dt

    def rk45_step(self, target_PG2):
        """RK4 method step"""
        state = [self.PG2, self.losses]

        k1 = self.ode_system(state, self.time, target_PG2)

        state2 = [state[0] + 0.5*self.dt*k1[0], state[1] + 0.5*self.dt*k1[1]]
        k2 = self.ode_system(state2, self.time + 0.5*self.dt, target_PG2)

        state3 = [state[0] + 0.5*self.dt*k2[0], state[1] + 0.5*self.dt*k2[1]]
        k3 = self.ode_system(state3, self.time + 0.5*self.dt, target_PG2)

        state4 = [state[0] + self.dt*k3[0], state[1] + self.dt*k3[1]]
        k4 = self.ode_system(state4, self.time + self.dt, target_PG2)

        self.PG2 += (self.dt / 6.0) * (k1[0] + 2*k2[0] + 2*k3[0] + k4[0])
        self.losses += (self.dt / 6.0) * (k1[1] + 2*k2[1] + 2*k3[1] + k4[1])
        self.time += self.dt

    def step(self, method='rk45'):
        """Advance simulation"""
        target_PG2 = 100.0 + np.sin(self.time * 0.5) * 50.0  # Varying load

        if method == 'euler':
            self.euler_step(target_PG2)
        else:
            self.rk45_step(target_PG2)

        # Update delta values based on current state
        self.delta_PG2 = max(1.0, abs(target_PG2 - 100.0))

        # Calculate results
        L2, _ = self.calculate_penalty_factor()
        inc_cost = self.calculate_incremental_cost()
        add_cost = self.calculate_additional_cost()

        # Store history
        self.time_history.append(self.time)
        self.PG2_history.append(self.PG2)
        self.losses_history.append(self.losses)
        self.L2_history.append(L2)
        self.incremental_cost_history.append(inc_cost)
        self.additional_cost_history.append(add_cost)

        # Limit history
        if len(self.time_history) > self.max_history:
            self.time_history.pop(0)
            self.PG2_history.pop(0)
            self.losses_history.pop(0)
            self.L2_history.pop(0)
            self.incremental_cost_history.pop(0)
            self.additional_cost_history.pop(0)

    def reset(self):
        """Reset simulation"""
        self.time = 0.0
        self.PG2 = 100.0
        self.losses = 10.0
        self.time_history = []
        self.PG2_history = []
        self.losses_history = []
        self.L2_history = []
        self.incremental_cost_history = []
        self.additional_cost_history = []


class Example319Simulator:
    """Example 3.19: Two-Plant Economic Dispatch"""

    def __init__(self):
        # Plant incremental costs
        self.dC1_dPG1 = 55.0  # Incremental cost at Plant-1 (Rs./MWh)
        self.dC2_dPG2 = 50.0  # Incremental cost at Plant-2 (Rs./MWh)
        self.lambda_sys = 75.0  # System lambda (Rs./MWh)

        # Dynamic parameters
        self.time = 0.0
        self.dt = 0.01

        # State variables
        self.PG1 = 100.0
        self.PG2 = 100.0
        self.load = 200.0

        # History
        self.max_history = 500
        self.time_history = []
        self.PG1_history = []
        self.PG2_history = []
        self.L1_history = []
        self.L2_history = []
        self.lambda_history = []

    def calculate_penalty_factors(self):
        """Calculate penalty factors for both plants"""
        L1 = self.lambda_sys / self.dC1_dPG1
        L2 = self.lambda_sys / self.dC2_dPG2
        return L1, L2

    def economic_dispatch(self, total_load):
        """Solve economic dispatch with penalty factors"""
        L1, L2 = self.calculate_penalty_factors()

        # For economic operation: dC1/dPG1 * L1 = dC2/dPG2 * L2 = lambda
        # This is already satisfied with the given incremental costs

        # Allocate load proportionally based on penalty factors
        # Higher penalty factor means plant is further from the load center
        # Lower incremental cost means cheaper plant

        # Simple allocation based on incremental costs
        total_inc_cost = self.dC1_dPG1 + self.dC2_dPG2
        PG1_target = total_load * (1.0 - self.dC1_dPG1/total_inc_cost)
        PG2_target = total_load * (1.0 - self.dC2_dPG2/total_inc_cost)

        return PG1_target, PG2_target

    def ode_system(self, state, t):
        """ODE system for dynamic dispatch"""
        PG1, PG2 = state

        # Varying load
        load = 200.0 + 50.0 * np.sin(t * 0.3)

        # Target power outputs
        PG1_target, PG2_target = self.economic_dispatch(load)

        # Dynamics
        tau = 2.0
        dPG1_dt = (PG1_target - PG1) / tau
        dPG2_dt = (PG2_target - PG2) / tau

        return [dPG1_dt, dPG2_dt]

    def euler_step(self):
        """Euler method step"""
        state = [self.PG1, self.PG2]
        derivatives = self.ode_system(state, self.time)

        self.PG1 += derivatives[0] * self.dt
        self.PG2 += derivatives[1] * self.dt
        self.time += self.dt

    def rk45_step(self):
        """RK4 method step"""
        state = [self.PG1, self.PG2]

        k1 = self.ode_system(state, self.time)

        state2 = [state[0] + 0.5*self.dt*k1[0], state[1] + 0.5*self.dt*k1[1]]
        k2 = self.ode_system(state2, self.time + 0.5*self.dt)

        state3 = [state[0] + 0.5*self.dt*k2[0], state[1] + 0.5*self.dt*k2[1]]
        k3 = self.ode_system(state3, self.time + 0.5*self.dt)

        state4 = [state[0] + self.dt*k3[0], state[1] + self.dt*k3[1]]
        k4 = self.ode_system(state4, self.time + self.dt)

        self.PG1 += (self.dt / 6.0) * (k1[0] + 2*k2[0] + 2*k3[0] + k4[0])
        self.PG2 += (self.dt / 6.0) * (k1[1] + 2*k2[1] + 2*k3[1] + k4[1])
        self.time += self.dt

    def step(self, method='rk45'):
        """Advance simulation"""
        if method == 'euler':
            self.euler_step()
        else:
            self.rk45_step()

        # Update load
        self.load = 200.0 + 50.0 * np.sin(self.time * 0.3)

        # Calculate penalty factors
        L1, L2 = self.calculate_penalty_factors()

        # Store history
        self.time_history.append(self.time)
        self.PG1_history.append(self.PG1)
        self.PG2_history.append(self.PG2)
        self.L1_history.append(L1)
        self.L2_history.append(L2)
        self.lambda_history.append(self.lambda_sys)

        # Limit history
        if len(self.time_history) > self.max_history:
            self.time_history.pop(0)
            self.PG1_history.pop(0)
            self.PG2_history.pop(0)
            self.L1_history.pop(0)
            self.L2_history.pop(0)
            self.lambda_history.pop(0)

    def reset(self):
        """Reset simulation"""
        self.time = 0.0
        self.PG1 = 100.0
        self.PG2 = 100.0
        self.load = 200.0
        self.time_history = []
        self.PG1_history = []
        self.PG2_history = []
        self.L1_history = []
        self.L2_history = []
        self.lambda_history = []


class EconomicDispatchGUI:
    """Main GUI application"""

    def __init__(self, root):
        self.root = root
        self.root.title("Power System Economic Dispatch - Examples 3.18 & 3.19")
        self.root.geometry("1600x900")
        self.root.minsize(1000, 700)

        # Simulators
        self.sim318 = Example318Simulator()
        self.sim319 = Example319Simulator()

        # Control variables
        self.running = False
        self.method = 'rk45'
        self.update_interval = 50
        self.current_tab = 0

        # Create UI
        self.create_ui()

        # Bind resize event
        self.root.bind('<Configure>', self.on_resize)

        # Start animation
        self.animate()

    def create_ui(self):
        """Create main user interface"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configure grid weights
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky='nsew')

        # Tab 1: Example 3.18
        self.tab318 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab318, text="Example 3.18: Penalty Factor")
        self.create_example318_tab(self.tab318)

        # Tab 2: Example 3.19
        self.tab319 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab319, text="Example 3.19: Two-Plant Dispatch")
        self.create_example319_tab(self.tab319)

        # Bind tab change
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)

    def create_example318_tab(self, parent):
        """Create Example 3.18 interface"""
        # Configure grid
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=3)

        # Left panel - controls
        control_frame = ttk.LabelFrame(parent, text="Controls - Example 3.18", padding=10)
        control_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Create scrollable controls
        canvas = tk.Canvas(control_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(control_frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Mousewheel scrolling
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        row = 0

        # Control buttons
        btn_frame = ttk.Frame(scroll_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=10, sticky='ew')

        self.start_btn_318 = ttk.Button(btn_frame, text="▶ Start", command=self.start_simulation)
        self.start_btn_318.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

        self.stop_btn_318 = ttk.Button(btn_frame, text="⏸ Pause", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_btn_318.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

        self.reset_btn_318 = ttk.Button(btn_frame, text="↻ Reset", command=lambda: self.reset_simulation(318))
        self.reset_btn_318.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

        row += 1

        # ODE Method
        ttk.Label(scroll_frame, text="ODE Solver:", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=(10,5), sticky='w')
        row += 1

        self.method_var = tk.StringVar(value='rk45')
        ttk.Radiobutton(scroll_frame, text="RK45", variable=self.method_var, value='rk45', command=self.update_method).grid(row=row, column=0, sticky='w')
        ttk.Radiobutton(scroll_frame, text="Euler", variable=self.method_var, value='euler', command=self.update_method).grid(row=row, column=1, sticky='w')
        row += 1

        # Lambda slider
        ttk.Separator(scroll_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky='ew', pady=10)
        row += 1

        ttk.Label(scroll_frame, text="System λ (Rs./MWh):", font=('Arial', 9, 'bold')).grid(row=row, column=0, columnspan=2, sticky='w')
        row += 1

        self.lambda_var_318 = tk.DoubleVar(value=60.0)
        lambda_slider = ttk.Scale(scroll_frame, from_=30.0, to=100.0, variable=self.lambda_var_318,
                                 orient=tk.HORIZONTAL, command=self.update_lambda_318)
        lambda_slider.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1

        self.lambda_label_318 = ttk.Label(scroll_frame, text="60.0 Rs./MWh")
        self.lambda_label_318.grid(row=row, column=0, columnspan=2)
        row += 1

        # Delta PG2 slider
        ttk.Label(scroll_frame, text="ΔP_G2 (kW):", font=('Arial', 9, 'bold')).grid(row=row, column=0, columnspan=2, sticky='w', pady=(10,0))
        row += 1

        self.delta_pg2_var = tk.DoubleVar(value=100.0)
        delta_pg2_slider = ttk.Scale(scroll_frame, from_=10.0, to=500.0, variable=self.delta_pg2_var,
                                     orient=tk.HORIZONTAL, command=self.update_delta_pg2)
        delta_pg2_slider.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1

        self.delta_pg2_label = ttk.Label(scroll_frame, text="100.0 kW")
        self.delta_pg2_label.grid(row=row, column=0, columnspan=2)
        row += 1

        # Delta PL slider
        ttk.Label(scroll_frame, text="ΔP_L (kW):", font=('Arial', 9, 'bold')).grid(row=row, column=0, columnspan=2, sticky='w', pady=(10,0))
        row += 1

        self.delta_pl_var = tk.DoubleVar(value=12.0)
        delta_pl_slider = ttk.Scale(scroll_frame, from_=1.0, to=100.0, variable=self.delta_pl_var,
                                    orient=tk.HORIZONTAL, command=self.update_delta_pl)
        delta_pl_slider.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1

        self.delta_pl_label = ttk.Label(scroll_frame, text="12.0 kW")
        self.delta_pl_label.grid(row=row, column=0, columnspan=2)
        row += 1

        # Results display
        ttk.Separator(scroll_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky='ew', pady=10)
        row += 1

        ttk.Label(scroll_frame, text="Results:", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, sticky='w')
        row += 1

        results_frame = ttk.Frame(scroll_frame)
        results_frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)

        self.results_text_318 = tk.Text(results_frame, height=15, width=35, wrap=tk.WORD, font=('Courier', 9))
        results_scrollbar = ttk.Scrollbar(results_frame, command=self.results_text_318.yview)
        self.results_text_318.configure(yscrollcommand=results_scrollbar.set)

        self.results_text_318.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row += 1

        scroll_frame.grid_columnconfigure(1, weight=1)

        # Right panel - plots
        plot_frame = ttk.Frame(parent)
        plot_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

        self.fig318 = Figure(figsize=(10, 8), facecolor='white')
        self.canvas318 = FigureCanvasTkAgg(self.fig318, plot_frame)
        self.canvas318.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Create subplots
        self.ax318_1 = self.fig318.add_subplot(2, 2, 1)
        self.ax318_2 = self.fig318.add_subplot(2, 2, 2)
        self.ax318_3 = self.fig318.add_subplot(2, 2, 3)
        self.ax318_4 = self.fig318.add_subplot(2, 2, 4)

        self.fig318.tight_layout(pad=3.0)

        # Initial update
        self.update_results_318()

    def create_example319_tab(self, parent):
        """Create Example 3.19 interface"""
        # Configure grid
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=3)

        # Left panel - controls
        control_frame = ttk.LabelFrame(parent, text="Controls - Example 3.19", padding=10)
        control_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Create scrollable controls
        canvas = tk.Canvas(control_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(control_frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Mousewheel scrolling
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        row = 0

        # Control buttons
        btn_frame = ttk.Frame(scroll_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=10, sticky='ew')

        self.start_btn_319 = ttk.Button(btn_frame, text="▶ Start", command=self.start_simulation)
        self.start_btn_319.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

        self.stop_btn_319 = ttk.Button(btn_frame, text="⏸ Pause", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_btn_319.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

        self.reset_btn_319 = ttk.Button(btn_frame, text="↻ Reset", command=lambda: self.reset_simulation(319))
        self.reset_btn_319.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

        row += 1

        # dC1/dPG1 slider
        ttk.Label(scroll_frame, text="dC₁/dP_G1 (Rs./MWh):", font=('Arial', 9, 'bold')).grid(row=row, column=0, columnspan=2, sticky='w', pady=(10,0))
        row += 1

        self.dc1_var = tk.DoubleVar(value=55.0)
        dc1_slider = ttk.Scale(scroll_frame, from_=30.0, to=100.0, variable=self.dc1_var,
                              orient=tk.HORIZONTAL, command=self.update_dc1)
        dc1_slider.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1

        self.dc1_label = ttk.Label(scroll_frame, text="55.0 Rs./MWh")
        self.dc1_label.grid(row=row, column=0, columnspan=2)
        row += 1

        # dC2/dPG2 slider
        ttk.Label(scroll_frame, text="dC₂/dP_G2 (Rs./MWh):", font=('Arial', 9, 'bold')).grid(row=row, column=0, columnspan=2, sticky='w', pady=(10,0))
        row += 1

        self.dc2_var = tk.DoubleVar(value=50.0)
        dc2_slider = ttk.Scale(scroll_frame, from_=30.0, to=100.0, variable=self.dc2_var,
                              orient=tk.HORIZONTAL, command=self.update_dc2)
        dc2_slider.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1

        self.dc2_label = ttk.Label(scroll_frame, text="50.0 Rs./MWh")
        self.dc2_label.grid(row=row, column=0, columnspan=2)
        row += 1

        # Lambda slider
        ttk.Label(scroll_frame, text="System λ (Rs./MWh):", font=('Arial', 9, 'bold')).grid(row=row, column=0, columnspan=2, sticky='w', pady=(10,0))
        row += 1

        self.lambda_var_319 = tk.DoubleVar(value=75.0)
        lambda_slider = ttk.Scale(scroll_frame, from_=40.0, to=120.0, variable=self.lambda_var_319,
                                 orient=tk.HORIZONTAL, command=self.update_lambda_319)
        lambda_slider.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1

        self.lambda_label_319 = ttk.Label(scroll_frame, text="75.0 Rs./MWh")
        self.lambda_label_319.grid(row=row, column=0, columnspan=2)
        row += 1

        # Results display
        ttk.Separator(scroll_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky='ew', pady=10)
        row += 1

        ttk.Label(scroll_frame, text="Results:", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, sticky='w')
        row += 1

        results_frame = ttk.Frame(scroll_frame)
        results_frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)

        self.results_text_319 = tk.Text(results_frame, height=15, width=35, wrap=tk.WORD, font=('Courier', 9))
        results_scrollbar = ttk.Scrollbar(results_frame, command=self.results_text_319.yview)
        self.results_text_319.configure(yscrollcommand=results_scrollbar.set)

        self.results_text_319.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row += 1

        scroll_frame.grid_columnconfigure(1, weight=1)

        # Right panel - plots
        plot_frame = ttk.Frame(parent)
        plot_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

        self.fig319 = Figure(figsize=(10, 8), facecolor='white')
        self.canvas319 = FigureCanvasTkAgg(self.fig319, plot_frame)
        self.canvas319.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Create subplots
        self.ax319_1 = self.fig319.add_subplot(2, 2, 1)
        self.ax319_2 = self.fig319.add_subplot(2, 2, 2)
        self.ax319_3 = self.fig319.add_subplot(2, 2, 3)
        self.ax319_4 = self.fig319.add_subplot(2, 2, 4)

        self.fig319.tight_layout(pad=3.0)

        # Initial update
        self.update_results_319()

    def update_lambda_318(self, value):
        """Update lambda for Example 3.18"""
        self.sim318.lambda_sys = self.lambda_var_318.get()
        self.lambda_label_318.config(text=f"{self.sim318.lambda_sys:.1f} Rs./MWh")
        self.update_results_318()

    def update_delta_pg2(self, value):
        """Update delta PG2"""
        self.sim318.delta_PG2 = self.delta_pg2_var.get()
        self.delta_pg2_label.config(text=f"{self.sim318.delta_PG2:.1f} kW")
        self.update_results_318()

    def update_delta_pl(self, value):
        """Update delta PL"""
        self.sim318.delta_PL = self.delta_pl_var.get()
        self.delta_pl_label.config(text=f"{self.sim318.delta_PL:.1f} kW")
        self.update_results_318()

    def update_dc1(self, value):
        """Update dC1/dPG1"""
        self.sim319.dC1_dPG1 = self.dc1_var.get()
        self.dc1_label.config(text=f"{self.sim319.dC1_dPG1:.1f} Rs./MWh")
        self.update_results_319()

    def update_dc2(self, value):
        """Update dC2/dPG2"""
        self.sim319.dC2_dPG2 = self.dc2_var.get()
        self.dc2_label.config(text=f"{self.sim319.dC2_dPG2:.1f} Rs./MWh")
        self.update_results_319()

    def update_lambda_319(self, value):
        """Update lambda for Example 3.19"""
        self.sim319.lambda_sys = self.lambda_var_319.get()
        self.lambda_label_319.config(text=f"{self.sim319.lambda_sys:.1f} Rs./MWh")
        self.update_results_319()

    def update_method(self):
        """Update ODE method"""
        self.method = self.method_var.get()

    def update_results_318(self):
        """Update results display for Example 3.18"""
        L2, dPL_dPG2 = self.sim318.calculate_penalty_factor()
        inc_cost = self.sim318.calculate_incremental_cost()
        add_cost = self.sim318.calculate_additional_cost()

        results = f"""EXAMPLE 3.18 RESULTS
{'='*40}

Given:
  System λ: {self.sim318.lambda_sys:.2f} Rs./MWh
  ΔP_G2: {self.sim318.delta_PG2:.2f} kW
  ΔP_L: {self.sim318.delta_PL:.2f} kW

Calculations:
  ∂P_L/∂P_G2 = {dPL_dPG2:.4f}

  Penalty Factor (L₂):
  L₂ = 1/(1 - ∂P_L/∂P_G2)
     = 1/(1 - {dPL_dPG2:.4f})
     = {L2:.4f}

  Incremental Cost at Plant-2:
  ∂C₂/∂P_G2 = λ/L₂
            = {self.sim318.lambda_sys:.2f}/{L2:.4f}
            = {inc_cost:.3f} Rs./MWh

  Additional Cost (for 1 MW increase):
  ΔC₂ = (∂C₂/∂P_G2) × ΔP_G2
      = {inc_cost:.3f} × 1.0
      = {add_cost:.3f} Rs./hr

{'='*40}
"""

        self.results_text_318.delete(1.0, tk.END)
        self.results_text_318.insert(1.0, results)

    def update_results_319(self):
        """Update results display for Example 3.19"""
        L1, L2 = self.sim319.calculate_penalty_factors()

        higher_pf = "Plant 2" if L2 > L1 else "Plant 1"

        results = f"""EXAMPLE 3.19 RESULTS
{'='*40}

Given:
  ∂C₁/∂P_G1: {self.sim319.dC1_dPG1:.2f} Rs./MWh
  ∂C₂/∂P_G2: {self.sim319.dC2_dPG2:.2f} Rs./MWh
  System λ: {self.sim319.lambda_sys:.2f} Rs./MWh

Economic Operation Condition:
  ∂C₁/∂P_G1 × L₁ = λ
  ∂C₂/∂P_G2 × L₂ = λ

Penalty Factors:
  L₁ = λ/(∂C₁/∂P_G1)
     = {self.sim319.lambda_sys:.2f}/{self.sim319.dC1_dPG1:.2f}
     = {L1:.4f}

  L₂ = λ/(∂C₂/∂P_G2)
     = {self.sim319.lambda_sys:.2f}/{self.sim319.dC2_dPG2:.2f}
     = {L2:.4f}

Conclusion:
  {higher_pf} has the higher
  penalty factor.

  L₁ = {L1:.4f}
  L₂ = {L2:.4f}

  Higher penalty factor indicates
  the plant is farther from the
  load center (higher losses).

{'='*40}
"""

        self.results_text_319.delete(1.0, tk.END)
        self.results_text_319.insert(1.0, results)

    def update_plots_318(self):
        """Update plots for Example 3.18"""
        if len(self.sim318.time_history) == 0:
            return

        times = np.array(self.sim318.time_history)
        PG2 = np.array(self.sim318.PG2_history)
        losses = np.array(self.sim318.losses_history)
        L2 = np.array(self.sim318.L2_history)
        inc_cost = np.array(self.sim318.incremental_cost_history)

        # Plot 1: Power Output
        self.ax318_1.clear()
        self.ax318_1.plot(times, PG2, 'b-', linewidth=2, label='Plant-2 Output')
        self.ax318_1.fill_between(times, 0, PG2, alpha=0.3, color='blue')
        self.ax318_1.set_title('Plant-2 Power Output', fontweight='bold', fontsize=10)
        self.ax318_1.set_xlabel('Time (s)', fontsize=9)
        self.ax318_1.set_ylabel('Power (MW)', fontsize=9)
        self.ax318_1.grid(True, alpha=0.3)
        self.ax318_1.legend(fontsize=8)

        # Plot 2: Losses
        self.ax318_2.clear()
        self.ax318_2.plot(times, losses, 'r-', linewidth=2, label='System Losses')
        self.ax318_2.fill_between(times, 0, losses, alpha=0.3, color='red')
        self.ax318_2.set_title('System Losses', fontweight='bold', fontsize=10)
        self.ax318_2.set_xlabel('Time (s)', fontsize=9)
        self.ax318_2.set_ylabel('Losses (MW)', fontsize=9)
        self.ax318_2.grid(True, alpha=0.3)
        self.ax318_2.legend(fontsize=8)

        # Plot 3: Penalty Factor
        self.ax318_3.clear()
        self.ax318_3.plot(times, L2, 'g-', linewidth=2, label='Penalty Factor L₂')
        self.ax318_3.fill_between(times, min(L2)*0.95, L2, alpha=0.3, color='green')
        self.ax318_3.set_title('Penalty Factor L₂', fontweight='bold', fontsize=10)
        self.ax318_3.set_xlabel('Time (s)', fontsize=9)
        self.ax318_3.set_ylabel('L₂', fontsize=9)
        self.ax318_3.grid(True, alpha=0.3)
        self.ax318_3.legend(fontsize=8)

        # Plot 4: Incremental Cost
        self.ax318_4.clear()
        self.ax318_4.plot(times, inc_cost, 'purple', linewidth=2, label='∂C₂/∂P_G2')
        self.ax318_4.fill_between(times, min(inc_cost)*0.95, inc_cost, alpha=0.3, color='purple')
        self.ax318_4.set_title('Incremental Cost at Plant-2', fontweight='bold', fontsize=10)
        self.ax318_4.set_xlabel('Time (s)', fontsize=9)
        self.ax318_4.set_ylabel('Rs./MWh', fontsize=9)
        self.ax318_4.grid(True, alpha=0.3)
        self.ax318_4.legend(fontsize=8)

        self.fig318.tight_layout(pad=3.0)
        self.canvas318.draw()

    def update_plots_319(self):
        """Update plots for Example 3.19"""
        if len(self.sim319.time_history) == 0:
            return

        times = np.array(self.sim319.time_history)
        PG1 = np.array(self.sim319.PG1_history)
        PG2 = np.array(self.sim319.PG2_history)
        L1 = np.array(self.sim319.L1_history)
        L2 = np.array(self.sim319.L2_history)

        # Plot 1: Power Outputs
        self.ax319_1.clear()
        self.ax319_1.plot(times, PG1, 'b-', linewidth=2, label='Plant-1')
        self.ax319_1.plot(times, PG2, 'r-', linewidth=2, label='Plant-2')
        self.ax319_1.fill_between(times, 0, PG1, alpha=0.3, color='blue')
        self.ax319_1.fill_between(times, PG1, PG1+PG2, alpha=0.3, color='red')
        self.ax319_1.set_title('Power Generation', fontweight='bold', fontsize=10)
        self.ax319_1.set_xlabel('Time (s)', fontsize=9)
        self.ax319_1.set_ylabel('Power (MW)', fontsize=9)
        self.ax319_1.grid(True, alpha=0.3)
        self.ax319_1.legend(fontsize=8)

        # Plot 2: Penalty Factors Comparison
        self.ax319_2.clear()
        self.ax319_2.plot(times, L1, 'b-', linewidth=2, label='L₁ (Plant-1)')
        self.ax319_2.plot(times, L2, 'r-', linewidth=2, label='L₂ (Plant-2)')
        self.ax319_2.set_title('Penalty Factors Comparison', fontweight='bold', fontsize=10)
        self.ax319_2.set_xlabel('Time (s)', fontsize=9)
        self.ax319_2.set_ylabel('Penalty Factor', fontsize=9)
        self.ax319_2.grid(True, alpha=0.3)
        self.ax319_2.legend(fontsize=8)

        # Plot 3: Total Load
        self.ax319_3.clear()
        total_gen = PG1 + PG2
        self.ax319_3.plot(times, total_gen, 'g-', linewidth=2, label='Total Generation')
        self.ax319_3.fill_between(times, 0, total_gen, alpha=0.3, color='green')
        self.ax319_3.set_title('Total System Generation', fontweight='bold', fontsize=10)
        self.ax319_3.set_xlabel('Time (s)', fontsize=9)
        self.ax319_3.set_ylabel('Power (MW)', fontsize=9)
        self.ax319_3.grid(True, alpha=0.3)
        self.ax319_3.legend(fontsize=8)

        # Plot 4: Current Distribution Pie Chart
        self.ax319_4.clear()
        if len(PG1) > 0:
            current_P1 = PG1[-1]
            current_P2 = PG2[-1]
            total = current_P1 + current_P2

            if total > 0:
                sizes = [current_P1, current_P2]
                labels = [f'Plant-1\n{current_P1:.1f} MW\n({current_P1/total*100:.1f}%)',
                         f'Plant-2\n{current_P2:.1f} MW\n({current_P2/total*100:.1f}%)']
                colors = ['#3498db', '#e74c3c']
                explode = (0.05, 0.05)

                self.ax319_4.pie(sizes, explode=explode, labels=labels, colors=colors,
                                autopct='', shadow=True, startangle=90)
                self.ax319_4.set_title(f'Power Distribution\nTotal: {total:.1f} MW',
                                      fontweight='bold', fontsize=10)

        self.fig319.tight_layout(pad=3.0)
        self.canvas319.draw()

    def animate(self):
        """Animation loop"""
        if self.running:
            tab_idx = self.notebook.index(self.notebook.select())

            if tab_idx == 0:  # Example 3.18
                self.sim318.step(method=self.method)
                self.update_plots_318()
                self.update_results_318()
            else:  # Example 3.19
                self.sim319.step(method=self.method)
                self.update_plots_319()
                self.update_results_319()

        self.root.after(self.update_interval, self.animate)

    def start_simulation(self):
        """Start simulation"""
        self.running = True
        self.start_btn_318.config(state=tk.DISABLED)
        self.stop_btn_318.config(state=tk.NORMAL)
        self.start_btn_319.config(state=tk.DISABLED)
        self.stop_btn_319.config(state=tk.NORMAL)

    def stop_simulation(self):
        """Stop simulation"""
        self.running = False
        self.start_btn_318.config(state=tk.NORMAL)
        self.stop_btn_318.config(state=tk.DISABLED)
        self.start_btn_319.config(state=tk.NORMAL)
        self.stop_btn_319.config(state=tk.DISABLED)

    def reset_simulation(self, example):
        """Reset simulation"""
        self.running = False

        if example == 318:
            self.sim318.reset()
            self.ax318_1.clear()
            self.ax318_2.clear()
            self.ax318_3.clear()
            self.ax318_4.clear()
            self.canvas318.draw()
            self.update_results_318()
        else:
            self.sim319.reset()
            self.ax319_1.clear()
            self.ax319_2.clear()
            self.ax319_3.clear()
            self.ax319_4.clear()
            self.canvas319.draw()
            self.update_results_319()

        self.start_btn_318.config(state=tk.NORMAL)
        self.stop_btn_318.config(state=tk.DISABLED)
        self.start_btn_319.config(state=tk.NORMAL)
        self.stop_btn_319.config(state=tk.DISABLED)

    def on_tab_changed(self, event):
        """Handle tab change"""
        pass

    def on_resize(self, event):
        """Handle window resize"""
        pass


def main():
    """Main entry point"""
    root = tk.Tk()
    app = EconomicDispatchGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
