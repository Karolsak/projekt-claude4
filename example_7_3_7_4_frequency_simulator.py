"""
Power System Frequency Simulator - Examples 7.3 and 7.4
Dynamic simulation with ODE solvers (RK45, Euler)
Tkinter GUI with automatic resizing, sliders, and real-time visualization
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import time


class FrequencySimulator:
    """
    Power System Frequency Simulator for Examples 7.3 and 7.4
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Power System Frequency Simulator - Examples 7.3 & 7.4")
        self.root.geometry("1400x900")

        # System parameters
        self.P_rated = 200.0  # MW
        self.H = 5.0  # kW-s/kVA
        self.Kps = 100.0  # Power system gain constant
        self.tps = 20.0  # Power system time constant (s)
        self.R = 3.0  # Speed regulation
        self.f0 = 50.0  # Normal frequency (Hz)
        self.tsg = 0.4  # Governor time constant (s)
        self.tt = 0.5  # Turbine time constant (s)

        # Simulation parameters
        self.delta_PL_percent = 0.5  # Load change percentage
        self.t_max = 100.0  # Simulation time (s)
        self.dt = 0.01  # Time step for Euler
        self.solver_method = "RK45"
        self.include_governor = False  # Example 7.3 by default

        # Simulation state
        self.is_running = False
        self.time_data = []
        self.freq_data = []
        self.current_time = 0.0
        self.state = None

        # Create GUI
        self.create_widgets()
        self.setup_plot()

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

    def create_widgets(self):
        """Create all GUI widgets with grid layout for automatic resizing"""

        # Configure root grid weights for resizing
        self.root.grid_rowconfigure(0, weight=0)  # Control frame
        self.root.grid_rowconfigure(1, weight=1)  # Plot frame
        self.root.grid_columnconfigure(0, weight=1)

        # Control Frame
        control_frame = ttk.LabelFrame(self.root, text="Control Panel", padding=10)
        control_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        # Configure control frame columns
        for i in range(6):
            control_frame.grid_columnconfigure(i, weight=1)

        # Example selection
        ttk.Label(control_frame, text="Example:").grid(row=0, column=0, sticky='e', padx=5)
        self.example_var = tk.StringVar(value="7.3")
        example_frame = ttk.Frame(control_frame)
        example_frame.grid(row=0, column=1, sticky='w', padx=5)
        ttk.Radiobutton(example_frame, text="7.3 (No Governor)",
                       variable=self.example_var, value="7.3",
                       command=self.on_example_change).pack(side='left')
        ttk.Radiobutton(example_frame, text="7.4 (With Governor)",
                       variable=self.example_var, value="7.4",
                       command=self.on_example_change).pack(side='left')

        # Solver selection
        ttk.Label(control_frame, text="Solver:").grid(row=0, column=2, sticky='e', padx=5)
        self.solver_var = tk.StringVar(value="RK45")
        solver_combo = ttk.Combobox(control_frame, textvariable=self.solver_var,
                                    values=["RK45", "Euler"], state='readonly', width=10)
        solver_combo.grid(row=0, column=3, sticky='w', padx=5)

        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=4, columnspan=2, sticky='e', padx=5)

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_simulation)
        self.start_button.pack(side='left', padx=2)

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_simulation, state='disabled')
        self.stop_button.pack(side='left', padx=2)

        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_simulation)
        self.reset_button.pack(side='left', padx=2)

        # Parameter sliders frame
        slider_frame = ttk.LabelFrame(self.root, text="System Parameters", padding=10)
        slider_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)

        # Configure slider frame for resizing
        slider_frame.grid_rowconfigure(0, weight=1)
        slider_frame.grid_columnconfigure(0, weight=1)
        slider_frame.grid_columnconfigure(1, weight=2)

        # Create canvas for sliders with scrollbar
        canvas_frame = ttk.Frame(slider_frame)
        canvas_frame.grid(row=0, column=0, sticky='nsew')
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        self.slider_canvas = tk.Canvas(canvas_frame, bg='white')
        scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=self.slider_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.slider_canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.slider_canvas.configure(scrollregion=self.slider_canvas.bbox("all"))
        )

        self.slider_canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        self.slider_canvas.configure(yscrollcommand=scrollbar.set)

        self.slider_canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Create sliders
        self.create_sliders()

        # Plot frame
        self.plot_frame = ttk.LabelFrame(slider_frame, text="Frequency Deviation", padding=5)
        self.plot_frame.grid(row=0, column=1, sticky='nsew', padx=5)
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.plot_frame.grid_columnconfigure(0, weight=1)

        # Results frame
        results_frame = ttk.LabelFrame(self.root, text="Results", padding=10)
        results_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=5)

        self.results_text = tk.Text(results_frame, height=4, wrap='word',
                                    font=('Courier', 9), bg='#f0f0f0')
        self.results_text.pack(fill='both', expand=True)

    def create_sliders(self):
        """Create parameter sliders"""

        self.sliders = {}

        slider_params = [
            ("Load Change ΔPL (%)", "delta_PL_percent", 0.1, 5.0, 0.5, 0.1),
            ("Inertia Constant H (kW-s/kVA)", "H", 1.0, 10.0, 5.0, 0.1),
            ("Power System Gain Kps", "Kps", 50.0, 200.0, 100.0, 1.0),
            ("Power System Time Constant tps (s)", "tps", 5.0, 40.0, 20.0, 1.0),
            ("Speed Regulation R", "R", 1.0, 10.0, 3.0, 0.1),
            ("Governor Time Constant tsg (s)", "tsg", 0.1, 2.0, 0.4, 0.1),
            ("Turbine Time Constant tt (s)", "tt", 0.1, 2.0, 0.5, 0.1),
            ("Simulation Time (s)", "t_max", 20.0, 200.0, 100.0, 10.0),
        ]

        for i, (label, param, min_val, max_val, default, resolution) in enumerate(slider_params):
            frame = ttk.Frame(self.scrollable_frame)
            frame.pack(fill='x', padx=5, pady=3)

            ttk.Label(frame, text=label, width=35).pack(side='left')

            value_label = ttk.Label(frame, text=f"{default:.2f}", width=8)
            value_label.pack(side='right', padx=5)

            slider = ttk.Scale(frame, from_=min_val, to=max_val, orient='horizontal',
                             command=lambda v, p=param, vl=value_label: self.update_slider(p, v, vl))
            slider.set(default)
            slider.pack(side='right', fill='x', expand=True, padx=5)

            self.sliders[param] = (slider, value_label)

    def update_slider(self, param, value, value_label):
        """Update slider value"""
        val = float(value)
        value_label.config(text=f"{val:.2f}")
        setattr(self, param, val)

    def on_example_change(self):
        """Handle example selection change"""
        self.include_governor = (self.example_var.get() == "7.4")
        self.reset_simulation()

    def setup_plot(self):
        """Setup matplotlib plot"""
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.ax.set_xlabel('Time (s)', fontsize=10)
        self.ax.set_ylabel('Frequency Deviation Δf (Hz)', fontsize=10)
        self.ax.set_title('Power System Frequency Response', fontsize=12, fontweight='bold')
        self.ax.grid(True, alpha=0.3)

        self.line, = self.ax.plot([], [], 'b-', linewidth=2, label='Δf(t)')
        self.ax.legend(loc='upper right')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def on_window_resize(self, event):
        """Handle window resize event"""
        # Only resize canvas if it's the root window being resized
        if event.widget == self.root:
            self.canvas.draw_idle()

    def system_dynamics_simple(self, t, state):
        """
        System dynamics for Example 7.3 (without governor and turbine)
        State: [Δf] in Hz
        """
        delta_f = state[0]  # Frequency deviation in Hz
        delta_PL = self.delta_PL_percent / 100.0  # Per unit load change

        # Equation: tps * dΔf/dt = -(1 + Kps/R) * Δf - Kps * ΔPL
        # Note: Δf is in Hz, ΔPL is in per unit
        d_delta_f = (-(1 + self.Kps / self.R) * delta_f - self.Kps * delta_PL) / self.tps

        return np.array([d_delta_f])

    def system_dynamics_governor(self, t, state):
        """
        System dynamics for Example 7.4 (with governor and turbine)
        State: [Δf (Hz), ΔPg (pu), ΔPm (pu)]
        """
        delta_f, delta_Pg, delta_Pm = state  # Δf in Hz, ΔPg and ΔPm in per unit
        delta_PL = self.delta_PL_percent / 100.0  # Per unit load change

        # Governor equation: tsg * dΔPg/dt = -Δf/R - ΔPg
        # Note: Δf is in Hz, so we use it directly
        d_delta_Pg = (-delta_f / self.R - delta_Pg) / self.tsg

        # Turbine equation: tt * dΔPm/dt = ΔPg - ΔPm
        d_delta_Pm = (delta_Pg - delta_Pm) / self.tt

        # Power system equation (with governor): tps * dΔf/dt = -Δf + Kps * (ΔPm - ΔPL)
        # Note: When governor is included, the droop effect (-Δf/R) is handled by governor feedback
        d_delta_f = (-delta_f + self.Kps * (delta_Pm - delta_PL)) / self.tps

        return np.array([d_delta_f, d_delta_Pg, d_delta_Pm])

    def euler_step(self, f, t, state, dt):
        """Euler method step"""
        return state + dt * f(t, state)

    def rk45_step(self, f, t, state, dt):
        """Runge-Kutta 4th order step (RK4 - simplified version of RK45)"""
        k1 = f(t, state)
        k2 = f(t + dt/2, state + dt*k1/2)
        k3 = f(t + dt/2, state + dt*k2/2)
        k4 = f(t + dt, state + dt*k3)

        return state + dt * (k1 + 2*k2 + 2*k3 + k4) / 6

    def integrate_step(self):
        """Perform one integration step"""
        if self.include_governor:
            dynamics = self.system_dynamics_governor
        else:
            dynamics = self.system_dynamics_simple

        if self.solver_var.get() == "RK45":
            self.state = self.rk45_step(dynamics, self.current_time, self.state, self.dt)
        else:  # Euler
            self.state = self.euler_step(dynamics, self.current_time, self.state, self.dt)

        self.current_time += self.dt

        # Store data (Δf is already in Hz)
        delta_f_hz = self.state[0]
        self.time_data.append(self.current_time)
        self.freq_data.append(delta_f_hz)

    def animate_simulation(self):
        """Animate the simulation"""
        if not self.is_running:
            return

        # Perform multiple steps for faster simulation
        steps_per_frame = 5
        for _ in range(steps_per_frame):
            if self.current_time >= self.t_max:
                self.stop_simulation()
                self.display_results()
                return

            self.integrate_step()

        # Update plot
        self.line.set_data(self.time_data, self.freq_data)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw_idle()

        # Schedule next frame
        self.root.after(10, self.animate_simulation)

    def start_simulation(self):
        """Start the simulation"""
        if self.is_running:
            return

        # Initialize state
        if self.include_governor:
            self.state = np.array([0.0, 0.0, 0.0])  # [Δf, ΔPg, ΔPm]
        else:
            self.state = np.array([0.0])  # [Δf]

        self.current_time = 0.0
        self.time_data = []
        self.freq_data = []

        self.is_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')

        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Simulation running...\n")

        # Start animation
        self.animate_simulation()

    def stop_simulation(self):
        """Stop the simulation"""
        self.is_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

    def reset_simulation(self):
        """Reset the simulation"""
        self.stop_simulation()

        self.time_data = []
        self.freq_data = []
        self.current_time = 0.0

        self.line.set_data([], [])
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

        self.results_text.delete(1.0, tk.END)

    def display_results(self):
        """Display simulation results"""
        if len(self.freq_data) == 0:
            return

        delta_f_ss = self.freq_data[-1]

        # Calculate expected values
        if self.include_governor:
            # Example 7.4 expected values
            expected_values = {
                0.5: -0.0235,
                1.0: -0.047,
            }
        else:
            # Example 7.3 expected values
            expected_values = {
                0.5: -0.0145,
                1.0: -0.029,
                2.0: -0.0583,
            }

        self.results_text.delete(1.0, tk.END)

        example_num = "7.4" if self.include_governor else "7.3"

        results = f"Example {example_num} Results:\n"
        results += f"{'='*60}\n"
        results += f"Load Change: {self.delta_PL_percent:.1f}%\n"
        results += f"Steady-State Frequency Deviation: Δfss = {delta_f_ss:.4f} Hz\n"

        # Find closest expected value
        closest_percent = min(expected_values.keys(),
                            key=lambda x: abs(x - self.delta_PL_percent))

        if abs(closest_percent - self.delta_PL_percent) < 0.1:
            expected = expected_values[closest_percent]
            error = abs(delta_f_ss - expected)
            results += f"Expected Value: Δfss = {expected:.4f} Hz\n"
            results += f"Error: {error:.4f} Hz ({100*error/abs(expected):.2f}%)\n"

        results += f"\nSolver: {self.solver_var.get()}\n"
        results += f"Time Step: {self.dt:.4f} s\n"
        results += f"Simulation Time: {self.current_time:.2f} s\n"

        self.results_text.insert(tk.END, results)


def main():
    """Main function"""
    root = tk.Tk()
    app = FrequencySimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
