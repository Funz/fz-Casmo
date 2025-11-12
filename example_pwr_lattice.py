#!/usr/bin/env python3
"""
Example script for running CASMO5 parametric studies with fz.

This example demonstrates how to use the fz-casmo plugin to run
a parametric study on a PWR lattice, varying enrichment and
temperatures to study burnup characteristics.
"""

import os
import sys

try:
    import fz
except ImportError:
    print("Error: fz framework not found.")
    print("Please install it from: https://github.com/Funz/fz")
    sys.exit(1)


def main():
    """Run a parametric study on PWR lattice burnup."""
    
    # Check if CASMO_PATH is set
    if 'CASMO_PATH' not in os.environ:
        print("Warning: CASMO_PATH environment variable is not set.")
        print("Please set it to your CASMO5 installation directory:")
        print("  export CASMO_PATH=/path/to/casmo5")
        print("\nFor demonstration purposes, setting a placeholder path...")
        os.environ['CASMO_PATH'] = '/opt/studsvik/casmo5'
        print("(You will need to update this for actual calculations)\n")
    
    # Define the input file
    input_file = "pwr_lattice.inp"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        print("Please run this script from the fz-casmo directory.")
        sys.exit(1)
    
    print("=" * 60)
    print("CASMO5 Parametric Study: PWR Lattice Burnup")
    print("=" * 60)
    print()
    
    # Define parameter values to study
    # Testing different enrichments and temperatures
    input_variables = {
        "enrichment": [3.0, 3.5, 4.0, 4.5],  # U-235 enrichment (%)
        "fuel_temp": 900,                     # Fuel temperature (K)
        "moderator_temp": 580,                # Moderator temperature (K)
        "burnup_steps": 50                    # Maximum burnup (MWd/kgU)
    }
    
    print("Parameters:")
    for var, values in input_variables.items():
        print(f"  {var}: {values}")
    print()
    
    print("Running calculations...")
    print("-" * 60)
    
    # Run the parametric study
    try:
        results = fz.fzr(
            input_path=input_file,
            input_variables=input_variables,
            model="CASMO",
            calculators="Localhost_CASMO",
            results_dir="results"
        )
        
        print()
        print("=" * 60)
        print("Results:")
        print("=" * 60)
        print()
        print(results)
        print()
        
        # Summary statistics
        print("-" * 60)
        print(f"Total calculations: {len(results)}")
        successful = len(results[results['status'] == 'done'])
        print(f"Successful: {successful}")
        print(f"Failed: {len(results) - successful}")
        
        # Analyze results if successful
        if successful > 0:
            print()
            print("Burnup Analysis:")
            print("-" * 60)
            for idx, row in results.iterrows():
                enr = row['enrichment']
                burnup = row.get('burnup', 'N/A')
                k_inf = row.get('k_inf', 'N/A')
                m2 = row.get('m2', 'N/A')
                if k_inf != 'N/A' and k_inf is not None:
                    print(f"  Enrichment={enr:.1f}%:")
                    print(f"    Burnup: {burnup}")
                    print(f"    k-inf: {k_inf}")
                    print(f"    M2: {m2}")
                else:
                    print(f"  Enrichment={enr:.1f}%: Calculation failed or incomplete")
        
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nMake sure you have:")
        print("1. The fz framework installed")
        print("2. CASMO5 installed and CASMO_PATH set correctly")
        print("3. The .fz/models and .fz/calculators directories present")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during calculation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("Study completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
