============================================================
Assignment 3: Producer-Consumer using Semaphores and Locks
Roll No: Ch21btech11034
============================================================
Files Included:
---------------
- prod_cons-sems-ch21btech11034.cpp: Source code for the semaphore-based solution.
- prod_cons-locks-ch21btech11034.cpp: Source code for the lock-based solution.
- run_experiments.py: Python script to automate experiments and generate plots.
- report.pdf: The detailed analysis report.

Compilation:
------------
Use g++ to compile the C++ source files. The -pthread flag is required.

1. Semaphore Version:
   g++ prod_cons-sems-ch21btech11034.cpp -o prod_cons-sems -lpthread -lrt

2. Lock Version:
   g++ prod_cons-locks-ch21btech11034.cpp -o prod_cons-locks -lpthread

Execution (C++ Programs):
-------------------------
Both compiled programs require an input file named inp-params.txt in the same directory.

1. Create inp-params.txt:
   The file should contain a single line with space-separated values:
   capacity np nc cntp cntc mu_p mu_c
   Example: 100 5 5 10 10 5.0 5.0

2. Run the compiled executable:
   ./prod_cons-sems inp-params.txt
   or
   ./prod_cons-locks inp-params.txt

Output:
-------
- The semaphore version creates/overwrites output_sems.txt.
- The lock version creates/overwrites output_locks.txt.

Execution (Python Experiment Script ):
-----------------------------------------------------
If experiments.py is used:
- Ensure Python 3, numpy, and matplotlib are installed .
- Make sure the C++ programs are compiled as prod_cons-sems and prod_cons-locks.
- Run the script: python3 run_experiments.py
- The script will automatically generate inp-params.txt, run the C++ executables for different scenarios, parse the results, and generate comparison plots (delay_ratio_comparison_log.png, thread_ratio_comparison_log.png).

============================================================