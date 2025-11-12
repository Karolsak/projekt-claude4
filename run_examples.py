#!/usr/bin/env python3
"""
Launcher script for Economic Dispatch Examples 3.18 & 3.19
Checks dependencies and provides helpful error messages
"""

import sys


def check_dependencies():
    """Check if required packages are installed"""
    required_packages = {
        'numpy': 'numpy',
        'matplotlib': 'matplotlib',
        'scipy': 'scipy',
        'tkinter': 'python3-tk (on Linux) or built-in with Python'
    }

    missing_packages = []

    print("Checking dependencies...\n")
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
        print("\n" + "="*70)
        print("Missing Dependencies Detected!")
        print("="*70)
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
            print("\nOn macOS, tkinter is included with Python from python.org")
            print("On Windows, tkinter is included with Python installer")
            print()

        print("After installing dependencies, run this script again.")
        print("="*70)
        return False

    return True


def main():
    """Main launcher"""
    print("="*70)
    print("  Power System Economic Dispatch Examples 3.18 & 3.19")
    print("  Real-Time ODE Solver with Interactive Visualization")
    print("="*70)
    print()

    if not check_dependencies():
        sys.exit(1)

    print("\n" + "="*70)
    print("All dependencies satisfied!")
    print("Launching application...")
    print("="*70 + "\n")

    # Import and run the main application
    try:
        import economic_dispatch_examples
        economic_dispatch_examples.main()
    except Exception as e:
        print(f"\nError launching application: {e}")
        import traceback
        traceback.print_exc()
        print("\nPlease check the error message above and ensure all")
        print("dependencies are properly installed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
