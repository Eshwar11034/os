

CXX      = g++
CXXFLAGS = -pthread -Wall

# Source and Executable Names
TAS_SRC      = assign2_TAS.cpp
CAS_SRC      = assign2_CAS.cpp
BOUND_SRC    = assign2_BoundedCAS.cpp
SEQ_SRC      = sequential.cpp
 
TAS_EXE      = assign2_TAS
CAS_EXE      = assign2_CAS
BOUND_EXE    = assign2_BoundedCAS
SEQ_EXE		 = assign2_sequential

# Default target: compile all executables
all: $(TAS_EXE) $(CAS_EXE) $(BOUND_EXE) $(SEQ_EXE)

$(TAS_EXE): $(TAS_SRC)
	$(CXX) $(CXXFLAGS) -o $@ $<

$(CAS_EXE): $(CAS_SRC)
	$(CXX) $(CXXFLAGS) -o $@ $<

$(BOUND_EXE): $(BOUND_SRC)
	$(CXX) $(CXXFLAGS) -o $@ $<

$(SEQ_EXE): $(SEQ_SRC)
	$(CXX) $(CXXFLAGS) -o $@ $<

# Optionally run the experiments (Python script must be in the same directory)
experiments:
	python3 experiments.py

# Optionally run the plotting script (if you have plot_from_csv.py)
plot:
	python3 plot_from_csv.py

# Clean up executables and temporary files
clean:
	rm -f $(TAS_EXE) $(CAS_EXE) $(BOUND_EXE) $(SEQ_EXE)
	rm -rf tmp_inputs

.PHONY: all experiments plot clean
