#!/usr/bin/env python3
"""
Launcher script for Power System ODE Simulator
Checks dependencies and provides helpful error messages
"""

import sys
import subprocess

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = {
        'numpy': 'numpy',
        'matplotlib': 'matplotlib',
        'tkinter': 'python3-tk (on Linux) or built-in with Python'
    }

    missing_packages = []

    for package, install_name in required_packages.items():
        try:
            if package == 'tkinter':
                __import__('tkinter')
            else:
                __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is NOT installed")
            missing_packages.append((package, install_name))

    if missing_packages:
        print("\n" + "="*60)
        print("Missing Dependencies Detected!")
        print("="*60)
        print("\nTo install missing packages, run:")
        print("\n  pip3 install --user", end="")
        for pkg, _ in missing_packages:
            if pkg != 'tkinter':
                print(f" {pkg}", end="")
        print("\n")

        if any(pkg == 'tkinter' for pkg, _ in missing_packages):
            print("For tkinter on Linux/Ubuntu, run:")
            print("  sudo apt-get install python3-tk")
            print("\nOr on Fedora/RHEL:")
            print("  sudo dnf install python3-tkinter")
            print()

        print("After installing dependencies, run this script again.")
        print("="*60)
        return False

    return True

def main():
    """Main launcher"""
    print("="*60)
    print("  Power System Economic Dispatch Simulator")
    print("  ODE Solver with Real-Time Visualization")
    print("="*60)
    print("\nChecking dependencies...\n")

    if not check_dependencies():
        sys.exit(1)

    print("\n" + "="*60)
    print("All dependencies satisfied!")
    print("Launching simulator...")
    print("="*60 + "\n")

    # Import and run the main application
    try:
        import power_system_ode_gui
        power_system_ode_gui.main()
    except Exception as e:
        print(f"\nError launching simulator: {e}")
        print("\nPlease check the error message above and ensure all")
        print("dependencies are properly installed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
