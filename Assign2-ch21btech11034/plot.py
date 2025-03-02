#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt

def plot_exp1(csv_file, output_file):
    df = pd.read_csv(csv_file)
    plt.figure()
    plt.plot(df["N"], df["TAS_total"].astype(float), marker='o', label="TAS")
    plt.plot(df["N"], df["CAS_total"].astype(float), marker='o', label="CAS")
    plt.plot(df["N"], df["BoundedCAS_total"].astype(float), marker='o', label="BoundedCAS")
    plt.plot(df["N"], df["Sequential_total"].astype(float), marker='o', label="Sequential_total")
    plt.xlabel("Sudoku Size (N)")
    plt.ylabel("Total Time (seconds)")
    plt.title("Experiment 1: Total Time vs. Sudoku Size")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_file, format="png", dpi=300)
    plt.close()
    print(f"Saved plot: {output_file}")

def plot_exp2(csv_file, output_file):
    df = pd.read_csv(csv_file)
    plt.figure()
    plt.plot(df["taskInc"], df["TAS_total"].astype(float), marker='o', label="TAS")
    plt.plot(df["taskInc"], df["CAS_total"].astype(float), marker='o', label="CAS")
    plt.plot(df["taskInc"], df["BoundedCAS_total"].astype(float), marker='o', label="BoundedCAS")
    plt.xlabel("Task Increment")
    plt.ylabel("Total Time (seconds)")
    plt.title("Experiment 2: Total Time vs. Task Increment")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_file, format="png", dpi=300)
    plt.close()
    print(f"Saved plot: {output_file}")

def plot_exp3(csv_file, output_file):
    df = pd.read_csv(csv_file)
    plt.figure()
    plt.plot(df["Threads"], df["TAS_total"].astype(float), marker='o', label="TAS")
    plt.plot(df["Threads"], df["CAS_total"].astype(float), marker='o', label="CAS")
    plt.plot(df["Threads"], df["BoundedCAS_total"].astype(float), marker='o', label="BoundedCAS")
    plt.xlabel("Number of Threads")
    plt.ylabel("Total Time (seconds)")
    plt.title("Experiment 3: Total Time vs. Number of Threads")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_file, format="png", dpi=300)
    plt.close()
    print(f"Saved plot: {output_file}")

def main():
    plot_exp1("exp1_results.csv", "exp1_plot.png")
    plot_exp2("exp2_results.csv", "exp2_plot.png")
    plot_exp3("exp3_results.csv", "exp3_plot.png")

if __name__ == "__main__":
    main()
