#!/usr/bin/env python3
"""
Root entry point to execute AIOps Sentinel telemetry simulators.
Usage:
    python run_simulator.py --scenario checkout_leak
    python run_simulator.py --scenario steady_state --ticks 10
"""
import sys
import os

# Add src/ to python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from simulators.cli import main

if __name__ == "__main__":
    main()
