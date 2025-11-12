# fz-casmo

FZ plugin for CASMO5 (Studsvik's advanced lattice physics code for Light Water Reactors).

This plugin enables parametric studies with CASMO5 using the [fz framework](https://github.com/Funz/fz).

## About CASMO5

CASMO5 is a high-fidelity lattice physics code developed by Studsvik for advanced simulation of nuclear fuel assemblies in Light Water Reactors (LWR), supporting both Pressurized Water Reactor (PWR) and Boiling Water Reactor (BWR) configurations. It provides detailed output at multiple burnup steps, including:

- **Burnup** (MWd/kgU) - Cumulative energy produced per mass of uranium
- **k-inf** - Infinite multiplication factor (neutron economy measure)
- **M2** - Macroscopic cross-section or migration area
- Additional outputs: isotope concentrations, cross-sections, pin powers, etc.

More information: https://www.studsvik.com/key-offerings/nuclear-simulation-software/software-products/casmo5/

## Features

* **Input File Support**: Standard CASMO5 input files (.inp, .cas)
* **Variable Syntax**: `$variable` for parameters (e.g., `$enrichment`)
* **Formula Syntax**: `@{...}` for calculated expressions
* **Comment Character**: `*` (asterisk)
* **Output Parsing**: Automatic extraction of burnup tables with k-inf, m2, and other burnup-dependent quantities

## Installation

### Prerequisites

1. **CASMO5 Installation**: You must have CASMO5 installed on your system (requires license from Studsvik)
2. **Python 3.7+**: Required for the fz framework
3. **fz framework**: Install from [github.com/Funz/fz](https://github.com/Funz/fz)

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/Funz/fz-casmo.git
   cd fz-casmo
   ```

2. Set the CASMO_PATH environment variable:
   ```bash
   # On Linux/Mac:
   export CASMO_PATH="/path/to/casmo5"
   
   # On Windows:
   set CASMO_PATH=C:\path\to\casmo5
   ```

3. The plugin is ready to use! The `.fz` directory contains:
   - `.fz/models/CASMO.json` - Model definition
   - `.fz/calculators/CASMO.sh` - Calculation script
   - `.fz/calculators/Localhost_CASMO.json` - Calculator configuration

## Usage

### Example: PWR Lattice Burnup Study

The repository includes a sample input file `pwr_lattice.inp` demonstrating a parametric study of a PWR 17x17 fuel assembly.

**Input file (`pwr_lattice.inp`):**
```casmo
* Sample CASMO5 input file for PWR lattice burnup calculation
* Variables: enrichment, fuel_temp, moderator_temp, burnup_steps

TTL * PWR 17x17 Assembly Parametric Study

PCA 1.26                    * Pin pitch in cm

* Material definitions
FUE 1 10.42/$enrichment     * UO2 fuel with variable enrichment
CLA 2 ZIRC4                 * Zircaloy-4 cladding
MOD 3 $moderator_temp/1.0   * Water moderator at variable temperature

PIN 1
1 0.4096                    * Fuel radius
2 0.418 0.475              * Cladding inner and outer radius
3                          * Moderator

LPI 17 1.26                * 17x17 lattice

STA
TFU=$fuel_temp            * Fuel temperature (K)
TMO=$moderator_temp       * Moderator temperature (K)
BOR=600                   * Boron concentration (ppm)

DEP -40
BUP
0 5 10 15 20 25 30 35 40 45 50

PRI 1
```

**Python script to run parametric study:**
```python
import fz
import os

# Set CASMO_PATH if not already set
os.environ['CASMO_PATH'] = '/opt/studsvik/casmo5'  # Adjust for your installation

# Define parameter values
input_variables = {
    "enrichment": [3.0, 3.5, 4.0, 4.5],  # U-235 enrichment (%)
    "fuel_temp": 900,                     # Fuel temperature (K)
    "moderator_temp": 580,                # Moderator temperature (K)
    "burnup_steps": 50                    # Maximum burnup (MWd/kgU)
}

# Run parametric study
results = fz.fzr(
    input_path="pwr_lattice.inp",
    input_variables=input_variables,
    model="CASMO",
    calculators="Localhost_CASMO",
    results_dir="results"
)

# Display results
print(results)
print(f"\nCompleted {len(results)} calculations")
```

**Expected output:**
```
   enrichment  fuel_temp  moderator_temp  burnup_steps     burnup     k_inf        m2  status        calculator
0         3.0        900             580            50  [0,5,10...]  [1.25...]  [15.8...]   done  Localhost_CASMO
1         3.5        900             580            50  [0,5,10...]  [1.28...]  [16.2...]   done  Localhost_CASMO
2         4.0        900             580            50  [0,5,10...]  [1.31...]  [16.5...]   done  Localhost_CASMO
3         4.5        900             580            50  [0,5,10...]  [1.34...]  [16.8...]   done  Localhost_CASMO

Completed 4 calculations
```

### Input File Syntax

#### Variables
Use `$variable_name` to define parameters:
```casmo
FUE 1 10.42/$enrichment     * UO2 fuel with variable enrichment
TFU=$fuel_temp              * Fuel temperature
TMO=$moderator_temp         * Moderator temperature
```

#### Formulas
Use `@{expression}` for calculated values:
```casmo
* Calculate total burnup steps
@{burnup_values = " ".join([str(i) for i in range(0, int($burnup_steps)+1, 5)])}
BUP
@{burnup_values}
```

#### Comments
CASMO5 comments start with `*` (asterisk):
```casmo
* This is a comment line in CASMO5 format
TTL * PWR Assembly Study  * Inline comment
```

### Output Files

CASMO5 produces several output files:
- `output.txt` - Main output file containing burnup tables and results
- `*.cax` - Binary cross-section library file
- `*.log` - Log file with calculation details

The plugin automatically extracts from output tables:
- **burnup**: Burnup values at each step (MWd/kgU)
- **k_inf**: Infinite multiplication factor at each burnup step
- **m2**: Migration area or macroscopic cross-section at each step

## Advanced Usage

### Using with Remote Calculators

Run CASMO5 on a remote server via SSH:

```python
import fz

results = fz.fzr(
    "pwr_lattice.inp",
    {"enrichment": [3.0, 3.5, 4.0, 4.5]},
    "CASMO",
    calculators="ssh://user@hpc.example.com/bash /path/to/fz-casmo/.fz/calculators/CASMO.sh",
    results_dir="remote_results"
)
```

### Using Cache for Reusing Results

```python
import fz

# First run
results1 = fz.fzr(
    "pwr_lattice.inp",
    {"enrichment": [3.0, 3.5, 4.0]},
    "CASMO",
    calculators="Localhost_CASMO",
    results_dir="run1"
)

# Second run with additional values - reuses previous results
results2 = fz.fzr(
    "pwr_lattice.inp",
    {"enrichment": [3.0, 3.5, 4.0, 4.5, 5.0]},  # Added 4.5 and 5.0
    "CASMO",
    calculators=[
        "cache://run1",          # Check cache first
        "Localhost_CASMO"        # Only run new cases
    ],
    results_dir="run2"
)
```

### Parallel Execution

Run multiple CASMO5 calculations in parallel:

```python
import fz

# Use multiple calculator instances for parallel execution
results = fz.fzr(
    "pwr_lattice.inp",
    {"enrichment": [x/10.0 for x in range(25, 55, 5)]},  # Many enrichment values
    "CASMO",
    calculators=["Localhost_CASMO"] * 4,  # 4 parallel workers
    results_dir="parallel_results"
)
```

## Model Configuration

The CASMO5 model is defined in `.fz/models/CASMO.json`:

```json
{
    "id": "CASMO",
    "varprefix": "$",
    "formulaprefix": "@",
    "delim": "{}",
    "commentline": "*",
    "output": {
        "burnup": "grep -A 1000 'BURNUP' output.txt | grep -E '^[[:space:]]*[0-9]' | awk '{print $1}'",
        "k_inf": "grep -A 1000 'BURNUP' output.txt | grep -E '^[[:space:]]*[0-9]' | awk '{print $2}'",
        "m2": "grep -A 1000 'BURNUP' output.txt | grep -E '^[[:space:]]*[0-9]' | awk '{print $3}'"
    }
}
```

You can customize this configuration to extract additional outputs from CASMO5 tables, such as:
- Isotope concentrations (U-235, Pu-239, etc.)
- Cross-sections (absorption, fission, etc.)
- Pin power distributions
- Discontinuity factors

## Troubleshooting

### CASMO5 not found
**Error**: `CASMO5 executable not found`

**Solution**: Set the `CASMO_PATH` environment variable:
```bash
export CASMO_PATH="/opt/studsvik/casmo5"
```

### License issues
**Error**: CASMO5 fails to run due to license

**Solution**: Ensure your CASMO5 license is valid and properly configured. Check with Studsvik support if needed.

### Output parsing fails
**Error**: `burnup`, `k_inf`, or `m2` returns None or empty values

**Solution**: 
1. Check that your CASMO5 input file produces tabular output
2. Verify the output format matches the parsing commands in `.fz/models/CASMO.json`
3. Examine the `output.txt` file in the results directory to see the actual CASMO5 output
4. Adjust the grep/awk commands in the model configuration to match your output format

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test your changes with actual CASMO5 calculations
4. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## License

This plugin follows the same license as the fz framework (BSD 3-Clause). See [LICENSE](LICENSE) file for details.

## Related Links

- [fz framework](https://github.com/Funz/fz) - Main parametric computing framework
- [CASMO5 Product Information](https://www.studsvik.com/key-offerings/nuclear-simulation-software/software-products/casmo5/) - Official CASMO5 page
- [Studsvik Scandpower](https://www.studsvik.com/) - CASMO5 developer

## Citation

If you use this plugin in your research, please cite:

```bibtex
@software{fz_casmo,
  title = {fz-casmo: CASMO5 Plugin for FZ Parametric Computing Framework},
  year = {2025},
  url = {https://github.com/Funz/fz-casmo}
}
```

## Sample Output Reference

The plugin is designed based on typical CASMO5 output tables as described in academic literature, such as:
- MIT OpenCourseWare: Systems Analysis of the Nuclear Fuel Cycle (22.251)
- CASMO-5 Development and Applications papers
- Various PWR and BWR lattice physics studies

Example output table structure:
```
BURNUP    K-INF    M2       (additional columns...)
0.000     1.225    15.8     ...
5.000     1.127    14.2     ...
10.000    1.045    13.1     ...
...
```