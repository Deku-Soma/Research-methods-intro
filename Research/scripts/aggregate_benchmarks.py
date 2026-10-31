#!/usr/bin/env python3
"""
Benchmark Statistical Aggregator
Reads benchmark_comparative_master.csv, calculates Mean ± Sample Standard Deviation,
min/max envelopes, and generates benchmark_statistical_summary.csv.
"""

import os
import csv
import numpy as np

def aggregate_results(csv_path, output_summary_path):
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return

    trials = []
    with open(csv_path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for r in reader:
            # Strip whitespace from keys and values
            row = {k.strip(): v.strip() for k, v in r.items() if k}
            trials.append(row)

    if not trials:
        print("No trial records found in CSV.")
        return

    # Group by (robot_model, scenario)
    groups = {}
    for r in trials:
        model = r.get('robot_model', 'unknown')
        scenario = r.get('scenario', 'unknown').replace('Trajectory: ', '')
        key = (model, scenario)
        if key not in groups:
            groups[key] = []
        groups[key].append(r)

    summary_rows = []

    print("\n" + "=" * 80)
    print("ROBOCUP SSL BENCHMARK STATISTICAL SUMMARY (Mean ± SD)")
    print("=" * 80)
    print(f"{'Robot Model':<18} | {'Scenario':<18} | {'N':<3} | {'Path RMSE (m)':<17} | {'v_max (m/s)':<14} | {'Status'}")
    print("-" * 80)

    for (model, scenario), records in sorted(groups.items()):
        n = len(records)
        rmses = [float(r['path_rmse']) for r in records if float(r.get('path_rmse', 0)) > 0]
        v_maxs = [float(r['v_max']) for r in records if float(r.get('v_max', 0)) > 0]
        t_stops = [float(r['t_stop']) for r in records if float(r.get('t_stop', 0)) > 0]
        d_stops = [float(r['d_stop']) for r in records if float(r.get('d_stop', 0)) > 0]
        passes = [1 for r in records if r.get('passed', '').lower() in ['true', '1']]

        pass_rate = (len(passes) / float(n)) * 100.0

        rmse_str = "N/A"
        if rmses:
            mean_r = np.mean(rmses)
            std_r = np.std(rmses, ddof=1) if len(rmses) > 1 else 0.0
            rmse_str = f"{mean_r:.4f} ± {std_r:.4f}"

        v_max_str = "N/A"
        if v_maxs:
            mean_v = np.mean(v_maxs)
            std_v = np.std(v_maxs, ddof=1) if len(v_maxs) > 1 else 0.0
            v_max_str = f"{mean_v:.3f} ± {std_v:.3f}"

        t_stop_str = "N/A"
        if t_stops:
            mean_t = np.mean(t_stops)
            std_t = np.std(t_stops, ddof=1) if len(t_stops) > 1 else 0.0
            t_stop_str = f"{mean_t:.3f} ± {std_t:.3f}"

        d_stop_str = "N/A"
        if d_stops:
            mean_d = np.mean(d_stops)
            std_d = np.std(d_stops, ddof=1) if len(d_stops) > 1 else 0.0
            d_stop_str = f"{mean_d:.3f} ± {std_d:.3f}"

        status_str = f"{pass_rate:.0f}% Pass"

        print(f"{model:<18} | {scenario:<18} | {n:<3} | {rmse_str:<17} | {v_max_str:<14} | {status_str}")

        summary_rows.append({
            'robot_model': model,
            'scenario': scenario,
            'trials_count': n,
            'path_rmse_mean_sd': rmse_str,
            'v_max_mean_sd': v_max_str,
            't_stop_mean_sd': t_stop_str,
            'd_stop_mean_sd': d_stop_str,
            'pass_rate_pct': f"{pass_rate:.1f}%"
        })

    print("=" * 80)

    # Write summary CSV
    with open(output_summary_path, 'w', newline='') as f:
        fieldnames = ['robot_model', 'scenario', 'trials_count', 'path_rmse_mean_sd', 'v_max_mean_sd', 't_stop_mean_sd', 'd_stop_mean_sd', 'pass_rate_pct']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"\nSaved statistical summary table to: {output_summary_path}\n")

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_dir = os.path.join(base_dir, 'benchmark_results')
    master_csv = os.path.join(results_dir, 'benchmark_comparative_master.csv')
    summary_csv = os.path.join(results_dir, 'benchmark_statistical_summary.csv')
    aggregate_results(master_csv, summary_csv)

