# Quick Start Guide

Get up and running with fz-casmo in 5 minutes!

## Prerequisites

- CASMO5 installed (with valid license)
- Python 3.7 or higher
- fz framework installed

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Funz/fz-casmo.git
   cd fz-casmo
   ```

2. **Install fz framework** (if not already installed):
   ```bash
   pip install funz-fz
   ```

3. **Set CASMO_PATH environment variable:**
   ```bash
   export CASMO_PATH="/path/to/your/casmo5"
   ```

## Your First Parametric Study

### Step 1: Create an Input File

Create a file `simple_case.inp`:

```casmo
* Simple PWR pin cell calculation
TTL * PWR Pin Cell Study

PCA 1.26                    * Pin pitch in cm
FUE 1 10.42/$enrichment     * UO2 fuel with variable enrichment
CLA 2 ZIRC4                 * Zircaloy-4 cladding
MOD 3 580/1.0               * Water moderator

PIN 1
1 0.4096                    * Fuel radius
2 0.418 0.475              * Cladding
3                          * Moderator

STA
TFU=900                    * Fuel temperature (K)
TMO=580                    * Moderator temperature (K)
BOR=600                    * Boron concentration (ppm)

DEP -40
BUP
0 10 20 30 40 50

PRI 1
```

### Step 2: Create a Python Script

Create `run_study.py`:

```python
import fz
import os

# Set CASMO path
os.environ['CASMO_PATH'] = '/opt/studsvik/casmo5'  # Adjust this!

# Run parametric study
results = fz.fzr(
    input_path="simple_case.inp",
    input_variables={
        "enrichment": [3.0, 4.0, 5.0]  # Three enrichment levels
    },
    model="CASMO",
    calculators="Localhost_CASMO",
    results_dir="results"
)

# Display results
print(results)
```

### Step 3: Run It!

```bash
python run_study.py
```

## What Happens?

1. fz reads your input template
2. Substitutes `$enrichment` with each value (3.0, 4.0, 5.0)
3. Runs CASMO5 for each case
4. Parses the output tables
5. Returns a DataFrame with results

## Example Output

```
   enrichment  fuel_temp  moderator_temp     burnup     k_inf        m2  status        calculator
0         3.0        900             580  [0,10,20...]  [1.25...]  [15.8...]   done  Localhost_CASMO
1         4.0        900             580  [0,10,20...]  [1.31...]  [16.5...]   done  Localhost_CASMO
2         5.0        900             580  [0,10,20...]  [1.37...]  [17.2...]   done  Localhost_CASMO
```

## Next Steps

- **Try the full example**: Run `python example_pwr_lattice.py`
- **Multiple variables**: Use lists for multiple parameters
- **Parallel execution**: Add more calculators for parallel runs
- **Cache results**: Use `cache://` to reuse previous calculations

## Common Issues

### CASMO not found
```bash
export CASMO_PATH="/correct/path/to/casmo5"
```

### Permission denied
```bash
chmod +x .fz/calculators/CASMO.sh
```

### No output parsed
- Check `results/*/output.txt` to see actual CASMO5 output
- Adjust parsing commands in `.fz/models/CASMO.json` if needed

## Learn More

- [Full README](README.md) - Complete documentation
- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [fz Framework](https://github.com/Funz/fz) - Main framework docs

Happy computing! 🚀
