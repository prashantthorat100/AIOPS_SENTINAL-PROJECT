"""
Command-line interface for AIOps Sentinel Telemetry Simulators.
"""
import argparse
import sys
import json
from .scenario_runner import ScenarioRunner


def main():
    parser = argparse.ArgumentParser(
        description="AIOps Sentinel Telemetry Simulators — Generate synthetic metrics, logs, traces, and K8s events."
    )
    parser.add_argument(
        "--scenario",
        choices=["checkout_leak", "steady_state"],
        default="checkout_leak",
        help="Scenario to execute (default: checkout_leak)",
    )
    parser.add_argument(
        "--output-dir",
        default="data/simulated",
        help="Directory to save simulated NDJSON telemetry (default: data/simulated)",
    )
    parser.add_argument(
        "--ticks",
        type=int,
        default=5,
        help="Number of ticks for steady_state scenario (default: 5)",
    )
    parser.add_argument(
        "--print-summary",
        action="store_true",
        default=True,
        help="Print summary table to console",
    )

    args = parser.parse_args()
    runner = ScenarioRunner()

    print(f"============================================================")
    print(f"[AIOps Sentinel] Telemetry Ingestion Simulator (P1)")
    print(f"============================================================")
    print(f"Selected scenario : {args.scenario}")
    print(f"Target directory  : {args.output_dir}")
    print(f"------------------------------------------------------------")

    if args.scenario == "checkout_leak":
        print("[*] Running 'checkout_memory_leak' (Sarah / checkout-service scenario)...")
        batches = runner.run_checkout_memory_leak_scenario()
    else:
        print(f"[*] Running 'steady_state' ({args.ticks} ticks)...")
        batches = runner.run_steady_state(num_ticks=args.ticks)

    counts = runner.export_scenario_to_disk(batches, output_dir=args.output_dir)

    print("\n[+] Simulation Completed Successfully!")
    print(f"------------------------------------------------------------")
    print(f"Generated batches       : {len(batches)}")
    print(f"Total metrics points    : {counts['metrics']}  (-> Kafka topic: metrics.raw)")
    print(f"Total log records       : {counts['logs']}  (-> Kafka topic: logs.raw)")
    print(f"Total trace spans       : {counts['traces']}  (-> Kafka topic: traces.raw)")
    print(f"Total Kubernetes events : {counts['k8s_events']}  (-> Kafka topic: events.k8s)")
    print(f"Total deployment events : {counts['deployments']}  (-> Kafka topic: events.deployments)")
    print(f"Saved to disk at        : {args.output_dir}/")
    print(f"============================================================\n")


if __name__ == "__main__":
    main()
