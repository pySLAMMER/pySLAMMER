#!/usr/bin/env python3
"""
Migration script to convert SLAMMER_results.xlsx to JSON format.
This is a one-time migration script for the verification system.
"""

import pandas as pd
import json
import gzip
from pathlib import Path
from datetime import datetime

def explore_excel_structure(excel_path):
    """Examine the structure of the Excel file to understand the data layout."""
    print("Examining Excel file structure...")
    
    # Load the Excel file
    df = pd.read_excel(excel_path)
    
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Look at unique values in key columns
    print(f"\nUnique earthquakes: {df['Earthquake'].nunique()}")
    print(f"Sample earthquakes: {df['Earthquake'].unique()[:5]}")
    
    print(f"\nUnique soil models: {df['soil model'].unique()}")
    print(f"Unique scaling types: {df['Scaling type'].unique()}")
    print(f"Unique scales: {df['Scale'].unique()}")
    
    # Check for missing values
    print(f"\nMissing values per column:")
    print(df.isnull().sum())
    
    # Look at a few complete rows
    print(f"\nSample row (first row):")
    for col in df.columns:
        print(f"  {col}: {df.iloc[0][col]}")
    
    print(f"\nSample row (row with coupled data - row 100):")
    for col in df.columns:
        print(f"  {col}: {df.iloc[100][col]}")
    
    return df

def create_test_record(row, method, row_index):
    """Create a single test record for a specific analysis method."""
    # Create unique test_id using row index and method
    test_id = f"test_{row_index:04d}_{method}"
    
    # Ground motion parameters
    # Map to the actual sample ground motion file
    earthquake_clean = row['Earthquake'].replace(' ', '_').replace('.', '')
    record_clean = row['Record']
    ground_motion_file = f"{earthquake_clean}_{record_clean}.csv"
    
    ground_motion = {
        "earthquake": row['Earthquake'],
        "record_file": row['Record'],
        "target_pga_g": row['Scale'],
        "ground_motion_file": ground_motion_file
    }
    
    # Analysis configuration
    analysis = {
        "method": method
    }
    
    # Site parameters - start with common ones
    site_params = {
        "ky_g": row['ky (g)']
    }
    
    # Method-specific site parameters and analysis mode
    if method in ['decoupled', 'coupled']:
        site_params.update({
            "height_m": row['height (m)'],
            "vs_slope_mps": row['Vs slope (m/s)'],
            "vs_base_mps": row['Vs base (m/s)'],
            "damping_ratio": row['Damping (--)']/100 if row['Damping (%)'] < 0 else row['Damping (--)']/100
        })
        
        analysis["mode"] = row['soil model']
        
        if row['soil model'] == 'equivalent_linear':
            site_params["reference_strain"] = row['Ref. strain']
    
    # Results
    normal_col = f'{method.title()} Normal (cm)'
    inverse_col = f'{method.title()} Inverse (cm)'
    
    results = {
        "normal_displacement_cm": row[normal_col],
        "inverse_displacement_cm": row[inverse_col]
    }
    
    # Add method-specific results
    if method in ['decoupled', 'coupled']:
        results.update({
            "kmax": row['kmax (g)'],
            "vs_final_mps": row['Vs (m/s)'],
            "damping_final": row['Damping (--)']
        })
    
    return {
        "test_id": test_id,
        "ground_motion_parameters": ground_motion,
        "analysis": analysis,
        "site_parameters": site_params,
        "results": results
    }

def migrate_to_json(df, output_path):
    """Convert the Excel data to JSON format matching our schema."""
    tests = []
    
    # Handle rigid analysis with deduplication
    rigid_seen = set()
    
    # Handle decoupled and coupled normally (no deduplication needed)
    for row_index, (_, row) in enumerate(df.iterrows()):
        # For rigid analysis, check if we've seen this combination before
        rigid_key = (row['Earthquake'], row['Record'], row['ky (g)'], row['Scale'])
        
        if rigid_key not in rigid_seen:
            rigid_test = create_test_record(row, 'rigid', row_index)
            tests.append(rigid_test)
            rigid_seen.add(rigid_key)
        
        # For decoupled and coupled, create records normally (no duplicates expected)
        for method in ['decoupled', 'coupled']:
            test_record = create_test_record(row, method, row_index)
            tests.append(test_record)
    
    # Create the complete JSON structure
    json_data = {
        "schema_version": "1.0",
        "metadata": {
            "source_program": "SLAMMER",
            "source_version": "1.1",
            "date_extracted": datetime.now().strftime("%Y-%m-%d"),
            "total_tests": len(tests),
            "description": f"Legacy SLAMMER results migrated from Excel format. Rigid tests deduplicated ({len(rigid_seen)} unique rigid tests from {len(df)} rows)."
        },
        "tests": tests
    }
    
    # Write to compressed JSON
    with gzip.open(output_path, 'wt', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"Migration complete!")
    print(f"  Original Excel rows: {len(df)}")
    print(f"  Unique rigid tests: {len(rigid_seen)}")
    print(f"  Decoupled tests: {len(df)}")
    print(f"  Coupled tests: {len(df)}")
    print(f"  Total JSON test records: {len(tests)}")
    print(f"  Output: {output_path}")
    
    return json_data

def main():
    excel_path = "/Users/lornearnold/GitHub/pySLAMMER/tests/SLAMMER_results.xlsx"
    output_path = "/Users/lornearnold/GitHub/pySLAMMER/tests/verification_data/reference/slammer_results.json.gz"
    
    # First, let's explore the structure
    print("=== EXPLORING EXCEL STRUCTURE ===")
    df = explore_excel_structure(excel_path)
    
    print("\n=== MIGRATING TO JSON ===")
    # Create output directory if it doesn't exist
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to JSON
    json_data = migrate_to_json(df, output_path)
    
    # Show a sample of the converted data
    print(f"\nSample converted test records:")
    print("Rigid test:")
    rigid_test = next(t for t in json_data['tests'] if t['analysis']['method'] == 'rigid')
    print(json.dumps(rigid_test, indent=2))
    
    print("\nDecoupled test:")
    decoupled_test = next(t for t in json_data['tests'] if t['analysis']['method'] == 'decoupled')
    print(json.dumps(decoupled_test, indent=2))

if __name__ == "__main__":
    main()