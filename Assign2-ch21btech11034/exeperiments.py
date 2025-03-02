#!/usr/bin/env python3
import subprocess
import time
import os
import math
import random
import re
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------
# Compilation Function
# ---------------------------
def compile_source(source_file, output_executable):
    """
    Compile the given C++ source file into an executable.
    Uses g++ with pthread support.
    """
    try:
        subprocess.check_call(["g++", source_file, "-o", output_executable, "-pthread"])
        print(f"Compilation of {source_file} succeeded. Executable: {output_executable}")
    except subprocess.CalledProcessError as e:
        print(f"Compilation of {source_file} failed with error: {e}")

# ---------------------------
# Sudoku Generator Functions
# ---------------------------
def pattern(r, c, n):
    # pattern for a baseline valid sudoku
    N = n * n
    return (n * (r % n) + r // n + c) % N

def shuffle(s):
    return random.sample(s, len(s))

def generate_sudoku(N):
    """
    Generate a complete valid sudoku puzzle.
    Here N must be a perfect square.
    """
    n = int(math.sqrt(N))
    if n * n != N:
        raise ValueError("Sudoku dimension must be a perfect square.")
    board = [[ (pattern(r, c, n) + 1) for c in range(N)] for r in range(N)]
    rows  = [ r for grp in shuffle(range(n)) for r in shuffle(range(grp*n, grp*n+n)) ]
    cols  = [ c for grp in shuffle(range(n)) for c in shuffle(range(grp*n, grp*n+n)) ]
    nums  = shuffle(list(range(1, N+1)))
    sudoku = [[ nums[board[r][c]-1] for c in cols ] for r in rows ]
    return sudoku

def write_input_file(filename, K, N, taskInc, sudoku):
    """
    Write the sudoku input file in the format:
    First line: K, N, taskInc.
    Followed by N lines of N space-separated numbers.
    """
    # Cap taskInc at N to avoid over-allocation issues
    if taskInc > N:
        taskInc = N
    with open(filename, 'w') as f:
        f.write(f"{K} {N} {taskInc}\n")
        for row in sudoku:
            f.write(" ".join(str(num) for num in row) + "\n")

# ---------------------------
# Experiment Runner Functions
# ---------------------------
def run_executable(executable, input_filename):
    """
    Run the given executable with the input file.
    Parse the output to extract multiple timing metrics.
    Expected output lines (for example):
      "The total time taken is X nanoseconds."
      "Average CS Entry Time is Y nanoseconds."
      "Average CS Exit Time is Z nanoseconds."
      "Worst-case CS Entry Time is A nanoseconds."
      "Worst-case CS Exit Time is B nanoseconds."
    Returns a dictionary with keys:
      total_time, avg_entry, avg_exit, worst_entry, worst_exit
    """
    try:
        output = subprocess.check_output([executable, input_filename], universal_newlines=True)
        metrics = {}
        m_total = re.search(r"total time taken is\s*([\d\.]+)\s*nanoseconds", output, re.IGNORECASE)
        if m_total: metrics["total_time"] = float(m_total.group(1)) / 1_000_000
        else: metrics["total_time"] = None
        m_avg_entry = re.search(r"Average CS Entry Time is\s*([\d\.]+)\s*nanoseconds", output, re.IGNORECASE)
        if m_avg_entry: metrics["avg_entry"] = float(m_avg_entry.group(1)) / 1_000_000
        else: metrics["avg_entry"] = None
        m_avg_exit = re.search(r"Average CS Exit Time is\s*([\d\.]+)\s*nanoseconds", output, re.IGNORECASE)
        if m_avg_exit: metrics["avg_exit"] = float(m_avg_exit.group(1)) / 1_000_000
        else: metrics["avg_exit"] = None
        m_worst_entry = re.search(r"Worst-case CS Entry Time is\s*([\d\.]+)\s*nanoseconds", output, re.IGNORECASE)
        if m_worst_entry: metrics["worst_entry"] = float(m_worst_entry.group(1)) / 1_000_000
        else: metrics["worst_entry"] = None
        m_worst_exit = re.search(r"Worst-case CS Exit Time is\s*([\d\.]+)\s*nanoseconds", output, re.IGNORECASE)
        if m_worst_exit: metrics["worst_exit"] = float(m_worst_exit.group(1)) / 1_000_000
        else: metrics["worst_exit"] = None
        return metrics
    except subprocess.CalledProcessError as e:
        print("Error running executable:", e)
        return None

def average_metrics(dicts):
    """
    Given a list of metrics dictionaries, average each metric.
    Returns a dictionary with the averaged metrics.
    """
    avg = {"total_time":0, "avg_entry":0, "avg_exit":0, "worst_entry":0, "worst_exit":0}
    count = len(dicts)
    for d in dicts:
        for key in avg.keys():
            if d[key] is not None:
                avg[key] += d[key]
    for key in avg.keys():
        avg[key] = avg[key] / count if count > 0 else None
    return avg

def average_over_runs(executable, input_filename, runs=5):
    metrics_list = []
    for i in range(runs):
        m = run_executable(executable, input_filename)
        if m is not None:
            metrics_list.append(m)
        else:
            print(f"Run {i} for {executable} failed.")
    return average_metrics(metrics_list) if metrics_list else None

# ---------------------------
# Plotting Functions
# ---------------------------
def plot_experiment(x_vals, y_vals, xlabel, ylabel, title, label, marker='o'):
    plt.plot(x_vals, y_vals, marker=marker, label=label)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)

# ---------------------------
# Function to Save Tables to File
# ---------------------------
def save_tables_to_file(results, exp1_sizes, exp2_taskInc_values, exp3_thread_values, filename="experiment_results_table.txt"):
    with open(filename, "w") as f:
        # For each experiment, we create a table where each row corresponds to an x-value
        # and each cell for a method shows: Total | AvgEntry | AvgExit | WorstEntry | WorstExit (all in nanoseconds)
        
        def format_metrics(metrics):
            if metrics is None:
                return "NA"
            return (f"{metrics['total_time']:.2f} | {metrics['avg_entry']:.2f} | "
                    f"{metrics['avg_exit']:.2f} | {metrics['worst_entry']:.2f} | "
                    f"{metrics['worst_exit']:.2f}")
        
        # Table header for Experiment 1
        f.write("Experiment 1: Time vs. Sudoku Size\n")
        header = "N\t" + "\t".join([f"{method}" for method in results.keys()]) + "\n"
        f.write(header)
        f.write("    (Total | AvgEntry | AvgExit | WorstEntry | WorstExit)\n")
        for N in exp1_sizes:
            row = f"{N}"
            for method in results.keys():
                metrics = results[method]["exp1"].get(N, None)
                row += f"\t{format_metrics(metrics)}"
            row += "\n"
            f.write(row)
        f.write("\n")
        
        # Table header for Experiment 2
        f.write("Experiment 2: Time vs. Task Increment\n")
        header = "taskInc\t" + "\t".join([f"{method}" for method in results.keys()]) + "\n"
        f.write(header)
        f.write("         (Total | AvgEntry | AvgExit | WorstEntry | WorstExit)\n")
        for t_inc in exp2_taskInc_values:
            row = f"{t_inc}"
            for method in results.keys():
                metrics = results[method]["exp2"].get(t_inc, None)
                row += f"\t{format_metrics(metrics)}"
            row += "\n"
            f.write(row)
        f.write("\n")
        
        # Table header for Experiment 3
        f.write("Experiment 3: Time vs. Number of Threads\n")
        header = "Threads\t" + "\t".join([f"{method}" for method in results.keys()]) + "\n"
        f.write(header)
        f.write("         (Total | AvgEntry | AvgExit | WorstEntry | WorstExit)\n")
        for threads in exp3_thread_values:
            row = f"{threads}"
            for method in results.keys():
                metrics = results[method]["exp3"].get(threads, None)
                row += f"\t{format_metrics(metrics)}"
            row += "\n"
            f.write(row)
    print(f"Tables saved in {filename}")

# ---------------------------
# Main Experiment Script
# ---------------------------
def main():
    # -------------
    # Compile All Three Versions
    # -------------
    source_files = {
        "TAS": "assign2_TAS.cpp",
        "CAS": "assign2_CAS.cpp",
        "BoundedCAS": "assign2_BoundedCAS.cpp",
        "Sequential": "sequential.cpp"
    }
    executables = {}
    for key, source in source_files.items():
        exe_name = f"assign2_{key}"
        compile_source(source, exe_name)
        executables[key] = "./" + exe_name  # assuming Unix-like system

    runs_per_point = 5

    # ---------------------------
    # Experiment Configurations
    # ---------------------------
    # Experiment 1: Vary sudoku size (N x N) with fixed threads and taskInc
    exp1_sizes = [400, 900, 1600, 2500, 3600, 4900, 6400, 8100, 10000]
    exp1_K = 8
    exp1_taskInc = 20

    # Experiment 2: Vary taskInc with fixed sudoku size and threads
    exp2_size = 8100  # using a 90x90 sudoku for a more intensive test
    exp2_K = 8
    exp2_taskInc_values = [10, 20, 30, 40, 50]

    # Experiment 3: Vary number of threads with fixed sudoku size and taskInc
    exp3_size = 8100  # using a 90x90 sudoku
    exp3_taskInc = 20
    exp3_thread_values = [1, 2, 4, 8, 16, 32]

    tmp_dir = "tmp_inputs"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    # Results structure: For each method, each experiment is a dict mapping x-value to averaged metrics.
    results = { method: { "exp1": {}, "exp2": {}, "exp3": {} } for method in executables.keys() }

    # ---------------------------
    # Experiment 1: Time vs. Sudoku Size
    # ---------------------------
    for N in exp1_sizes:
        sudoku = generate_sudoku(N)
        input_filename = os.path.join(tmp_dir, f"exp1_N{N}.txt")
        write_input_file(input_filename, exp1_K, N, exp1_taskInc, sudoku)
        for key, exe in executables.items():
            avg_metrics = average_over_runs(exe, input_filename, runs=runs_per_point)
            print(f"Method {key} | Experiment 1: N={N}, Metrics = {avg_metrics}")
            results[key]["exp1"][N] = avg_metrics

    # ---------------------------
    # Experiment 2: Time vs. Task Increment
    # ---------------------------
    sudoku = generate_sudoku(exp2_size)
    for t_inc in exp2_taskInc_values:
        input_filename = os.path.join(tmp_dir, f"exp2_taskInc{t_inc}.txt")
        write_input_file(input_filename, exp2_K, exp2_size, t_inc, sudoku)
        for key, exe in executables.items():
            avg_metrics = average_over_runs(exe, input_filename, runs=runs_per_point)
            print(f"Method {key} | Experiment 2: taskInc={t_inc}, Metrics = {avg_metrics}")
            results[key]["exp2"][t_inc] = avg_metrics

    # ---------------------------
    # Experiment 3: Time vs. Number of Threads
    # ---------------------------
    sudoku = generate_sudoku(exp3_size)
    for threads in exp3_thread_values:
        input_filename = os.path.join(tmp_dir, f"exp3_threads{threads}.txt")
        write_input_file(input_filename, threads, exp3_size, exp3_taskInc, sudoku)
        for key, exe in executables.items():
            avg_metrics = average_over_runs(exe, input_filename, runs=runs_per_point)
            print(f"Method {key} | Experiment 3: Threads={threads}, Metrics = {avg_metrics}")
            results[key]["exp3"][threads] = avg_metrics

    # ---------------------------
    # Save Tables to File
    # ---------------------------
    save_tables_to_file(results, exp1_sizes, exp2_taskInc_values, exp3_thread_values)

    # ---------------------------
    # Plotting the Results - Separate Files
    # ---------------------------
    methods = list(executables.keys())
    
    # For plotting, we can simply plot the total time for each experiment.
    # Experiment 1 Plot: Total Time vs. Sudoku Size
    plt.figure()
    for method in methods:
        total_times = [results[method]["exp1"][N]["total_time"] for N in exp1_sizes]
        plot_experiment(exp1_sizes, total_times, "Sudoku Size (N x N)", "Total Time (μs)",
                        "Exp 1: Total Time vs. Sudoku Size", label=method)
    plt.legend()
    plt.tight_layout()
    plt.savefig("exp1_plot.png", format="png", dpi=300)
    plt.close()
    
    # Experiment 2 Plot: Total Time vs. Task Increment
    plt.figure()
    for method in methods:
        total_times = [results[method]["exp2"][t_inc]["total_time"] for t_inc in exp2_taskInc_values]
        plot_experiment(exp2_taskInc_values, total_times, "Task Increment", "Total Time (μs)",
                        "Exp 2: Total Time vs. Task Increment", label=method)
    plt.legend()
    plt.tight_layout()
    plt.savefig("exp2_plot.png", format="png", dpi=300)
    plt.close()
    
    # Experiment 3 Plot: Total Time vs. Number of Threads
    plt.figure()
    for method in methods:
        total_times = [results[method]["exp3"][threads]["total_time"] for threads in exp3_thread_values]
        plot_experiment(exp3_thread_values, total_times, "Number of Threads", "Total Time (μs)",
                        "Exp 3: Total Time vs. Number of Threads", label=method)
    plt.legend()
    plt.tight_layout()
    plt.savefig("exp3_plot.png", format="png", dpi=300)
    plt.close()

if __name__ == "__main__":
    main()
