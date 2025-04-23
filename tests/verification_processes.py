import numpy as np
import pandas as pd

import pyslammer as slam

# df = pd.read_excel("SLAMMER_results.xlsx")
pySLAMMER_columns = [
    "rigid_norm_pyslammer",
    "rigid_inverse_pyslammer",
    "rigid_avg_pyslammer",
    "decoupled_norm_pyslammer",
    "decoupled_inverse_pyslammer",
    "decoupled_avg_pyslammer",
    "coupled_norm_pyslammer",
    "coupled_inverse_pyslammer",
    "coupled_avg_pyslammer",
]

SLAMMER_columns = [
    "Rigid Normal (cm)",
    "Rigid Inverse (cm)",
    "Rigid Average (cm)",
    "Decoupled Normal (cm)",
    "Decoupled Inverse (cm)",
    "Decoupled Average (cm)",
    "Coupled Normal (cm)",
    "Coupled Inverse (cm)",
    "Coupled Average (cm)",
]


def import_verification_data(file_path, auto_update=True):
    """
    Import verification data from an Excel file.
    """
    # Read the Excel file
    df = pd.read_excel(file_path)

    ps_count = pySLAMMER_runs(df)
    s_count = len(df)

    if auto_update:
        # Check if the number of pySLAMMER runs matches the number of SLAMMER runs
        if ps_count != s_count:
            update_comparison(df, file_path)

    if ps_count != s_count:
        raise Warning(
            f"""Number of pySLAMMER runs ({ps_count}) does not match the number of SLAMMER runs ({s_count}).
            Consider updating the pySLAMMER results"""
        )
    formatted_df = reformat_data(df)
    return formatted_df


def pySLAMMER_runs(df):
    """
    Count the number of pySLAMMER runs in the DataFrame.
    """
    # Count the number of rows with non-null values in the pySLAMMER columns

    return df[pySLAMMER_columns].notnull().any(axis=1).sum()


def update_comparison(df, file_path):
    size = len(df)
    motions = slam.sample_ground_motions()
    for index, row in df.iterrows():
        # Skip rows already containing pySLAMMER results
        if not pd.isna(row[pySLAMMER_columns[0]]):
            continue
        motion_key = f"{row['Earthquake'].replace(' ', '_').replace('.', '').replace(',', '')}_{row['Record'].replace('.', '')}"
        motion = motions[motion_key]

        # Get the rigid inputs
        rigid_inputs = {
            "ky": row["ky (g)"],
            "a_in": motion.accel,
            "dt": motion.dt,
            "target_pga": row["Scale"],
        }
        flexible_inputs = {
            "damp_ratio": row["Damping (%)"] / 100,
            "ref_strain": row["Ref. strain"] / 100,
            "soil_model": row["soil model"],
            "height": row["height (m)"],
            "vs_slope": row["Vs slope (m/s)"],
            "vs_base": row["Vs base (m/s)"],
        }

        # Run the simulation in the normal direction
        rigid_normal = slam.RigidAnalysis(**rigid_inputs)
        decoupled_normal = slam.Decoupled(**rigid_inputs, **flexible_inputs)
        coupled_normal = slam.Coupled(**rigid_inputs, **flexible_inputs)

        # invert the input motion to match range of SLAMMER results
        rigid_inputs["a_in"] = -rigid_inputs["a_in"]

        # Run again (in the inverse direction)
        rigid_inverse = slam.RigidAnalysis(**rigid_inputs)
        decoupled_inverse = slam.Decoupled(**rigid_inputs, **flexible_inputs)
        coupled_inverse = slam.Coupled(**rigid_inputs, **flexible_inputs)

        # Add the results max displacment (in cm) to the dataframe
        df.at[index, pySLAMMER_columns[0]] = rigid_normal.max_sliding_disp * 100
        df.at[index, pySLAMMER_columns[1]] = rigid_inverse.max_sliding_disp * 100
        df.at[index, pySLAMMER_columns[2]] = (
            np.mean([rigid_normal.max_sliding_disp, rigid_inverse.max_sliding_disp])
            * 100
        )

        df.at[index, pySLAMMER_columns[3]] = decoupled_normal.max_sliding_disp * 100
        df.at[index, pySLAMMER_columns[4]] = decoupled_inverse.max_sliding_disp * 100
        df.at[index, pySLAMMER_columns[5]] = (
            np.mean(
                [decoupled_normal.max_sliding_disp, decoupled_inverse.max_sliding_disp]
            )
            * 100
        )

        df.at[index, pySLAMMER_columns[6]] = coupled_normal.max_sliding_disp * 100
        df.at[index, pySLAMMER_columns[7]] = coupled_inverse.max_sliding_disp * 100
        df.at[index, pySLAMMER_columns[8]] = (
            np.mean([coupled_normal.max_sliding_disp, coupled_inverse.max_sliding_disp])
            * 100
        )

        # After Rathje and Bray (1999) use the max decoupled HEA for common k_max for flexible simulations
        df.at[index, "k_max_out"] = np.max(decoupled_normal.HEA)

        # store the input values for reproducibility
        df.at[index, "rigid_input"] = (
            f"ky: {rigid_inputs['ky']}, dt: {rigid_inputs['dt']}, target_pga: {rigid_inputs['target_pga']}"
        )
        df.at[index, "flexible_input"] = (
            f"damp_ratio: {flexible_inputs['damp_ratio']}, ref_strain: {flexible_inputs['ref_strain']}, soil_model: {flexible_inputs['soil_model']}, height: {flexible_inputs['height']}, vs_slope: {flexible_inputs['vs_slope']}, vs_base: {flexible_inputs['vs_base']}"
        )

    # Save the updated DataFrame back to the Excel file
    new_size = len(df)
    df.to_excel(file_path, index=False)
    print(
        f"Updated {new_size - size} rows in {file_path} with pySLAMMER results."
        f" Total rows: {new_size}."
    )


def reformat_data(df):
    # once the file has been re-saved, no need to preserve the empty columns
    df = df.dropna(axis=1, how="all")

    # Set up the data catogores and labels
    methods = ["Rigid", "Decoupled", "Coupled"]
    directions = ["Normal", "Inverse", "Average"]
    column_mapping = {
        SLAMMER_columns[0]: ("SLAMMER", methods[0], directions[0]),
        SLAMMER_columns[1]: ("SLAMMER", methods[0], directions[1]),
        SLAMMER_columns[2]: ("SLAMMER", methods[0], directions[2]),
        SLAMMER_columns[3]: ("SLAMMER", methods[1], directions[0]),
        SLAMMER_columns[4]: ("SLAMMER", methods[1], directions[1]),
        SLAMMER_columns[5]: ("SLAMMER", methods[1], directions[2]),
        SLAMMER_columns[6]: ("SLAMMER", methods[2], directions[0]),
        SLAMMER_columns[7]: ("SLAMMER", methods[2], directions[1]),
        SLAMMER_columns[8]: ("SLAMMER", methods[2], directions[2]),
        pySLAMMER_columns[0]: ("pySLAMMER", methods[0], directions[0]),
        pySLAMMER_columns[1]: ("pySLAMMER", methods[0], directions[1]),
        pySLAMMER_columns[2]: ("pySLAMMER", methods[0], directions[2]),
        pySLAMMER_columns[3]: ("pySLAMMER", methods[1], directions[0]),
        pySLAMMER_columns[4]: ("pySLAMMER", methods[1], directions[1]),
        pySLAMMER_columns[5]: ("pySLAMMER", methods[1], directions[2]),
        pySLAMMER_columns[6]: ("pySLAMMER", methods[2], directions[0]),
        pySLAMMER_columns[7]: ("pySLAMMER", methods[2], directions[1]),
        pySLAMMER_columns[8]: ("pySLAMMER", methods[2], directions[2]),
    }

    # Preserve columns not in the mapping
    preserve_columns = [col for col in df.columns if col not in column_mapping]

    # Create a new dataframe to store the melted data
    melted_data = []

    # Process each row
    for row_idx, row in df.iterrows():
        preserved_values = {col: row[col] for col in preserve_columns}

        # Process each column that needs melting
        for col_name, value in row.items():
            if col_name in column_mapping:
                a_col, b_val, c_val = column_mapping[col_name]
                new_row = {a_col: value, "Method": b_val, "Direction": c_val}
                new_row.update(preserved_values)
                melted_data.append(new_row)

    # Create the new dataframe
    result_df = pd.DataFrame(melted_data)
    # create dataframe where SLAMMER column is not null
    SLAMMER_df = result_df[result_df["SLAMMER"].notnull()]
    # create dataframe where pySLAMMER column is not null
    pySLAMMER_df = result_df[result_df["pySLAMMER"].notnull()]
    # merge the two dataframes where Method and Direction are the same
    # Perform an inner merge on the specified columns

    to_match = [
        "Earthquake",
        "Record",
        "Method",
        "Direction",
        "rigid_input",
        "flexible_input",
    ]
    merged_df = SLAMMER_df.merge(
        pySLAMMER_df[["pySLAMMER"] + to_match],
        on=to_match,
        how="left",
        suffixes=("_DELETE", ""),
    )
    # Drop the columns with _DELETE suffix
    merged_df = merged_df.loc[:, ~merged_df.columns.str.endswith("_DELETE")]

    # Remove duplicate rigid analyses for when only flexible inputs were varied
    duplicate_check_columns = [
        "Earthquake",
        "Record",
        "Method",
        "Direction",
        "rigid_input",
    ]

    filtered_df = merged_df[
        ~(
            (merged_df["Method"] == "Rigid")
            & (merged_df.duplicated(subset=duplicate_check_columns, keep="first"))
        )
    ]

    return filtered_df


# df = filtered_df
# df["kykmax"] = df["ky (g)"] / df["kmax (g)"]
