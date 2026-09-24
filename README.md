# fz-Casmo

[fz](https://github.com/Funz/fz) wrapper for **CASMO5**, Studsvik's lattice physics
code for light water reactors: parametric lattice calculations (enrichment, state
point, depletion...) run locally, over SSH or on SLURM.

For core calculations with SIMULATE, and the CASMO → CMS-LINK → SIMULATE chain, see
[fz-Simulate](https://github.com/Funz/fz-Simulate).

## Requirements

- fz ≥ 1.2 (`pip install funz-fz`)
- a licensed CASMO5 installation, reachable through one of (first match wins):
  - `CASMO_CMD`: full launcher command, e.g. `export CASMO_CMD=/opt/studsvik/bin/cas5`
  - `CASMO_PATH`: install directory containing `cas5` or `bin/cas5` (also sets `CMSHOME`)
  - `cas5` on `PATH`
- `CASMO_OPTS`: options given to the launcher (default `-p -k`; set it to an empty
  string to pass none)

## Quick start

```bash
fz install model Casmo            # installs .fz/models/CASMO.json + calculator alias
fzi examples/CASMO/input.inp --model CASMO --format json
fzr examples/CASMO/input.inp --model CASMO \
    --input_variables '{"enrichment": [3.0, 3.5, 4.0, 4.5]}' --format json
```

```python
import fz
results = fz.fzr("examples/CASMO/input.inp",
                 {"enrichment": [3.0, 3.5, 4.0, 4.5], "boron": [0, 1000]},
                 model="CASMO", results_dir="results")
print(results[["enrichment", "boron", "k_inf", "status"]])
```

No `--calculators` argument is needed: the installed `localhost_CASMO` alias is found
automatically. For remote runs, add an alias with the same `models` key, e.g.
`.fz/calculators/cluster_CASMO.json`:

```json
{ "uri": "slurm://user@cluster:batch", "models": { "CASMO": "bash /path/to/CASMO.sh" } }
```

## Input syntax

| Element | Syntax | Example |
|---|---|---|
| variable | `${name}` or `${name~default}` | `FUE 1 10.4/${enrichment~4.0}` |
| formula | `@{expression}` (Python) | `@{heavy_density(${theoretical_density~0.95})}` |
| formula context | `*@ ...` (a CASMO comment line) | `*@ def heavy_density(td): return round(10.96 * td, 3)` |
| comment | `*` | |

`examples/CASMO/input.inp` is an **illustrative** PWR 17x17 depletion deck with
variables `enrichment`, `theoretical_density`, `fuel_temp`, `moderator_temp`, `boron`,
`power_density`, `burnup_max` (all with defaults). Check the card syntax against the
CASMO5 manual of your version before production use.

## Outputs

Parsed from the `*.out` file(s) of each case:

| Output | Content |
|---|---|
| `k_inf` | k-infinity: list per burnup step (depletion summary of `*_dep.out`), else last value |
| `burnup` | burnup per step [MWd/kg] (depletion summary) |
| `m2` | migration area [cm²] |
| `pin_power_peak` | pin power peaking factor |
| `u235_wt_pct`, `fissile_pu_wt_pct`, `total_pu_wt_pct` | isotopic contents per step |
| `num_burnup_steps`, `dep_target` | depletion metadata |
| `pin_power`, `pin_exposure` | 2D pin maps (last edit) |
| `beta_eff`, `neutron_generation_time`, `decay_constants` | kinetics parameters |
| `hist_void`, `hist_tfu`, `hist_tmo`, `hist_bor` | history state variables |
| `cax_files` | names of the `*.cax` files produced (input to CMS-LINK) |

**Validation status:** the output parsers have not yet been checked against a
reference set of real CASMO5 outputs. `tests/fixtures/` is where such outputs go (see
below); until then, check the parsed values against your own `.out` files.

## Tests

```bash
pip install funz-fz pytest
pytest tests/
```

The tests run the fz CLI without CASMO5:

- `tests/mock/cas5` is a fake launcher (k-inf = 0.9 + 0.1 × enrichment) used to check the
  runner, alias discovery and error handling end to end;
- every `tests/fixtures/<case>/` holding an `expected.json` is parsed with `fzo` and
  compared with it. To validate the parsers on real results, add a directory with a
  CASMO5 `.out` file (an excerpt is enough) and the expected values:

  ```
  tests/fixtures/pwr17_dep/input_dep.out
  tests/fixtures/pwr17_dep/expected.json   {"k_inf": [1.30012, ...], "burnup": [0.0, ...]}
  ```

`tests/fixtures/synthetic_dep/` is hand-written in the layout the parsers assume; it
is not a CASMO5 output.

## Layout

```
.fz/models/CASMO.json                 model: syntax + output parsers
.fz/calculators/CASMO.sh              runner (locates cas5, runs it, checks the .out)
.fz/calculators/localhost_CASMO.json  local calculator alias
examples/CASMO/input.inp              parametric example deck
tests/                                mock launcher, fixtures, pytest suite
```

## License

BSD 3-Clause License. See [LICENSE](LICENSE).
