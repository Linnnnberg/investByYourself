#!/usr/bin/env python3
"""
UI Launcher - investByYourself

A simple launcher script to run different UI components of our platform.
This makes it easy to test and demonstrate our financial tools.

Usage:
    python run_ui.py                    # Run main app
    python run_ui.py portfolio          # Run portfolio dashboard
    python run_ui.py calculator         # Run financial calculator
    python run_ui.py charts             # Run chart viewer
"""

import os
import subprocess
import sys


def main():
    """Main launcher function."""
    if len(sys.argv) < 2:
        # No arguments, run main app
        run_component("src/ui/main_app.py")
    else:
        component = sys.argv[1].lower()

        if component in ["portfolio", "dashboard"]:
            run_component("src/ui/portfolio_dashboard.py")
        elif component in ["calculator", "calc"]:
            run_component("src/ui/financial_calculator.py")
        elif component in ["charts", "chart", "viewer"]:
            run_component("src/ui/chart_viewer.py")
        elif component in ["main", "home"]:
            run_component("src/ui/main_app.py")
        else:
            print(f"Unknown component: {component}")
            print_usage()
            sys.exit(1)


def run_component(component_path):
    """Run a specific UI component using Streamlit."""
    if not os.path.exists(component_path):
        print(f"❌ Component not found: {component_path}")
        print("Make sure you're running this from the project root directory.")
        sys.exit(1)

    print(f"🚀 Launching {component_path}...")
    print("📱 Streamlit will open in your default web browser")
    print("🔗 If it doesn't open automatically, go to: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)

    try:
        # Run the component using Streamlit
        subprocess.run(["streamlit", "run", component_path])
    except KeyboardInterrupt:
        print("\n👋 UI server stopped by user")
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install it first:")
        print("   pip install streamlit")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running component: {e}")
        sys.exit(1)


def print_usage():
    """Print usage information."""
    print(
        """
📱 InvestByYourself UI Launcher

Usage:
    python run_ui.py                    # Run main app (default)
    python run_ui.py portfolio          # Run portfolio dashboard
    python run_ui.py calculator         # Run financial calculator
    python run_ui.py charts             # Run chart viewer
    python run_ui.py main               # Run main app

Available Components:
    📊 portfolio/dashboard  - Portfolio management and tracking
    🧮 calculator/calc      - Financial calculations and tools
    📈 charts/viewer        - Chart viewing and analysis
    🏠 main/home            - Main platform launcher

Examples:
    python run_ui.py portfolio          # Launch portfolio dashboard
    python run_ui.py calc               # Launch financial calculator
    python run_ui.py                    # Launch main app
    """
    )


if __name__ == "__main__":
    main()
