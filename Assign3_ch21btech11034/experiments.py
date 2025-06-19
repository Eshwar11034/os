#!/usr/bin/env python3
import subprocess
import os
import re
import time
import matplotlib.pyplot as plt
import numpy as np


SEM_EXEC = "./prod_cons-sems"     
LOCK_EXEC = "./prod_cons-locks"   

SEM_OUTPUT = "output_sems.txt"   
LOCK_OUTPUT = "output_locks.txt"  

CAPACITY = 100
NUM_TRIALS = 3 


def write_input_file(capacity, np_val, nc_val, cntp, cntc, mu_p, mu_c):
    """Writes the parameters to inp-params.txt"""
    with open("inp-params.txt", "w") as f:
      
        f.write(f"{int(capacity)} {int(np_val)} {int(nc_val)} {int(cntp)} {int(cntc)} {mu_p} {mu_c}\n") # Ensure ints where needed

def run_experiment(executable, output_file):
    """Runs the specified C++ executable and waits for completion."""
    if os.path.exists(output_file):
        os.remove(output_file)
    try:
        result = subprocess.run(
            [executable, "inp-params.txt"], 
            capture_output=True, text=True, check=True, timeout=120 
        ) 
    except subprocess.CalledProcessError as e:
        print(f"Error running {executable}: {e}")
        print(f"Stderr: {e.stderr}")
        return None 
    except subprocess.TimeoutExpired:
        print(f"Timeout running {executable}")
        return None 
    except FileNotFoundError:
        print(f"Error: Executable {executable} not found. Make sure it is compiled and in the current directory.")
        exit(1) 

    time.sleep(0.1) 
    if not os.path.exists(output_file):
        print(f"Error: Output file {output_file} was not created by {executable}.")
        return None 
    return output_file

def parse_cs_times(output_file):
    """
    Parses the output file to extract average critical section (CS) times in milliseconds.
    Expected lines:
      PROD_CS: <thread_id> <cs_entry_ns> <cs_exit_ns>
      CONS_CS: <thread_id> <cs_entry_ns> <cs_exit_ns>
    """
    prod_times_ms = []
    cons_times_ms = []
    if output_file is None: 
        return 0, 0 
        
    try:
        with open(output_file, "r") as f:
            for line in f:
                line = line.strip()
                parts = line.split()
                try:
                    if line.startswith("PROD_CS:") and len(parts) >= 4:
                        cs_entry_ns = int(parts[2])
                        cs_exit_ns  = int(parts[3])
                        prod_times_ms.append((cs_exit_ns - cs_entry_ns) / 1_000_000.0) 
                    elif line.startswith("CONS_CS:") and len(parts) >= 4:
                        cs_entry_ns = int(parts[2])
                        cs_exit_ns  = int(parts[3])
                        cons_times_ms.append((cs_exit_ns - cs_entry_ns) / 1_000_000.0) 
                except (ValueError, IndexError):
                    continue
    except FileNotFoundError:
        print(f"Error: Could not open {output_file} for parsing.")
        return 0, 0

    avg_prod_ms = np.mean(prod_times_ms) if prod_times_ms else 0
    avg_cons_ms = np.mean(cons_times_ms) if cons_times_ms else 0
    return avg_prod_ms, avg_cons_ms

def run_trials(executable, output_file, trials=NUM_TRIALS):
    """Runs the experiment multiple times and averages the CS times."""
    prod_list = []
    cons_list = []
    print(f"  Running {executable} ({trials} trials)...")
    for i in range(trials):
        print(f"    Trial {i+1}/{trials}...")
        actual_output_file = run_experiment(executable, output_file)
        if actual_output_file:
             avg_prod, avg_cons = parse_cs_times(actual_output_file)
             prod_list.append(avg_prod)
             cons_list.append(avg_cons)
        else:
             print(f"    Trial {i+1} failed for {executable}. Skipping.")

    
    if not prod_list or not cons_list:
        print(f"  All trials failed for {executable}.")
        return 0, 0

    mean_prod = np.mean(prod_list)
    mean_cons = np.mean(cons_list)
    print(f"  ...done. Avg CS Time: Prod={mean_prod:.4f} ms, Cons={mean_cons:.4f} ms (over {len(prod_list)} successful trials)")
    return mean_prod, mean_cons

def run_delay_ratio_experiment():
    """
    Experiment 1: Vary Delay Ratio mu_p/mu_c.
    Uses fixed cntp=100, cntc=100, and fixed mu_p=10ms.
    Calculates mu_c based on the ratio.
    """
    print("\n--- Starting Experiment 1: Delay Ratio (Fixed mu_p) ---")
  
    ratios = [10.0, 5.0, 1.0, 0.5, 0.1]
    np_val = 5 
    nc_val = 5
    cntp = 100 
    cntc = 100 
    fixed_mu_p = 10.0 

    delay_ratios_used = [] 
    sem_prod_times_ms = []
    sem_cons_times_ms = []
    lock_prod_times_ms = []
    lock_cons_times_ms = []

    for r in ratios:
        if r <= 0:
            print(f"Skipping invalid ratio: {r}")
            continue
        mu_c = fixed_mu_p / r
        mu_p = fixed_mu_p 

        print(f"\nRunning for Delay Ratio: mu_p/mu_c = {r} (np={np_val}, nc={nc_val}, cntp={cntp}, cntc={cntc}, mu_p={mu_p} ms [fixed], mu_c={mu_c:.2f} ms [calc])")
        delay_ratios_used.append(r) 
        write_input_file(CAPACITY, np_val, nc_val, cntp, cntc, mu_p, mu_c)

        avg_sem_prod, avg_sem_cons = run_trials(SEM_EXEC, SEM_OUTPUT, trials=NUM_TRIALS)
        sem_prod_times_ms.append(avg_sem_prod)
        sem_cons_times_ms.append(avg_sem_cons)

        avg_lock_prod, avg_lock_cons = run_trials(LOCK_EXEC, LOCK_OUTPUT, trials=NUM_TRIALS)
        lock_prod_times_ms.append(avg_lock_prod)
        lock_cons_times_ms.append(avg_lock_cons)

    print("--- Experiment 1 Complete ---")
    return delay_ratios_used, sem_prod_times_ms, sem_cons_times_ms, lock_prod_times_ms, lock_cons_times_ms

def run_thread_ratio_experiment():
    """
    Experiment 2: Vary Thread Number Ratio np/nc.
    Uses fixed cntp=100 and calculates cntc to balance total items.
    Note: Total work varies significantly between configurations.
    """
    print("\n--- Starting Experiment 2: Thread Ratio (Fixed cntp) ---")
    configs = [
        (10.0, 10, 1),
        (5.0,  5,  1),
        (1.0,  5,  5),  
        (0.5,  1,  2),
        (0.1,  1, 10),
    ]
    
    mu_p = 10.0
    mu_c = 10.0
    fixed_cntp = 100 

    ratios = []
    sem_prod_times_ms = []
    sem_cons_times_ms = []
    lock_prod_times_ms = []
    lock_cons_times_ms = []

    for ratio, np_val, nc_val in configs:
        total_produced = np_val * fixed_cntp
        if total_produced % nc_val != 0:
             print(f"Warning: Total items produced ({total_produced}) not cleanly divisible by nc ({nc_val}) for ratio {ratio}. Check config.")
        
        cntc = total_produced // nc_val 
        
      
        cntp = fixed_cntp 

        print(f"\nRunning for Thread Ratio: np/nc = {ratio} (np={np_val}, nc={nc_val}, cntp={cntp} [fixed], cntc={cntc} [calc], mu_p={mu_p} ms, mu_c={mu_c} ms)")
        ratios.append(ratio)
        write_input_file(CAPACITY, np_val, nc_val, cntp, cntc, mu_p, mu_c)

        avg_sem_prod, avg_sem_cons = run_trials(SEM_EXEC, SEM_OUTPUT, trials=NUM_TRIALS)
        sem_prod_times_ms.append(avg_sem_prod)
        sem_cons_times_ms.append(avg_sem_cons)

        avg_lock_prod, avg_lock_cons = run_trials(LOCK_EXEC, LOCK_OUTPUT, trials=NUM_TRIALS)
        lock_prod_times_ms.append(avg_lock_prod)
        lock_cons_times_ms.append(avg_lock_cons)

    print("--- Experiment 2 Complete ---")
    
   
    sorted_results = sorted(zip(ratios, sem_prod_times_ms, sem_cons_times_ms, lock_prod_times_ms, lock_cons_times_ms))
    if not sorted_results: 
         print("Warning: No valid thread ratio configurations were run.")
         return [], [], [], [], []
         
    ratios_sorted, sem_prod_sorted, sem_cons_sorted, lock_prod_sorted, lock_cons_sorted = zip(*sorted_results)
    
    return list(ratios_sorted), list(sem_prod_sorted), list(sem_cons_sorted), list(lock_prod_sorted), list(lock_cons_sorted)


def plot_comparison_experiment(x_values,
                              sem_prod_times, sem_cons_times,
                              lock_prod_times, lock_cons_times,
                              xlabel, title_prefix, filename_prefix):
    """Plots all four curves (Sem Prod/Cons, Lock Prod/Cons) on a single graph,
       using a logarithmic scale for the Y-axis to show differences near zero."""
       
    if not x_values or not any(sem_prod_times + sem_cons_times + lock_prod_times + lock_cons_times): # Check if there's any data at all
        print(f"No valid data to plot for {title_prefix}.")
        return

    plt.figure(figsize=(10, 7))

    def safe_log_plot(x, y, **kwargs):
        valid_indices = [i for i, val in enumerate(y) if val > 0]
        if not valid_indices:
            print(f"Warning: No positive data points for label '{kwargs.get('label', '')}'. Cannot plot on log scale.")
            return 
        
        x_filtered = [x[i] for i in valid_indices]
        y_filtered = [y[i] for i in valid_indices]
        plt.plot(x_filtered, y_filtered, **kwargs)

    safe_log_plot(x_values, sem_prod_times, marker='o', linestyle='-', color='blue', label='Producer (Semaphores)')
    safe_log_plot(x_values, sem_cons_times, marker='s', linestyle='-', color='cyan', label='Consumer (Semaphores)')
    safe_log_plot(x_values, lock_prod_times, marker='^', linestyle='--', color='red', label='Producer (Locks)')
    safe_log_plot(x_values, lock_cons_times, marker='x', linestyle='--', color='magenta', label='Consumer (Locks)') 

    plt.xlabel(xlabel)
    plt.ylabel("Average Critical Section Time (ms) [Log Scale]") 
    plt.title(f"{title_prefix}: Average CS Time Comparison")

    plt.yscale('log')

    all_positive_times = [t for t in sem_prod_times + sem_cons_times + lock_prod_times + lock_cons_times if t > 0]
    if all_positive_times:
         min_val = min(all_positive_times)
         plt.ylim(bottom=min_val * 0.1) 
    if "Ratio" in xlabel and max(x_values, default=1) / min(x_values, default=1) > 10:
         plt.xscale('log')
         try:
             plt.xticks(x_values, labels=[f"{x:.2g}" for x in x_values]) # Format labels nicely
         except ValueError as e:
              print(f"Warning: Could not set custom x-ticks for log scale. Matplotlib defaults will be used. Error: {e}")
              pass 
    else:
         plt.xticks(x_values)


    plt.legend()
    plt.grid(True, which="both", ls="--", alpha=0.6)
    plt.tight_layout()

    filename = f"{filename_prefix}_comparison_log.png" #
    plt.savefig(filename)
    print(f"Log scale plot saved to {filename}")
    plt.show()
def main():
    if not os.path.exists(SEM_EXEC) or not os.path.exists(LOCK_EXEC):
        print(f"Error: Make sure executables '{SEM_EXEC}' and '{LOCK_EXEC}' exist.")
        print("Compile the C++ files first (see example commands in script).")
        return

    (delay_ratios, sem_prod_delay, sem_cons_delay,
     lock_prod_delay, lock_cons_delay) = run_delay_ratio_experiment()
    plot_comparison_experiment(
        x_values=delay_ratios,
        sem_prod_times=sem_prod_delay, sem_cons_times=sem_cons_delay,
        lock_prod_times=lock_prod_delay, lock_cons_times=lock_cons_delay,
        xlabel="Delay Ratio (μp / μc)",
        title_prefix="Delay Ratio Experiment",
        filename_prefix="delay_ratio"
    )

    (thread_ratios, sem_prod_thread, sem_cons_thread,
     lock_prod_thread, lock_cons_thread) = run_thread_ratio_experiment()
    plot_comparison_experiment(
        x_values=thread_ratios,
        sem_prod_times=sem_prod_thread, sem_cons_times=sem_cons_thread,
        lock_prod_times=lock_prod_thread, lock_cons_times=lock_cons_thread,
        xlabel="Thread Number Ratio (np / nc)",
        title_prefix="Thread Ratio Experiment",
        filename_prefix="thread_ratio"
    )

    print("\nAll experiments and plotting complete.")

if __name__ == "__main__":
    main()