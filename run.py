import os
import pandas as pd
from datetime import datetime
from write_rhem_parameter_file import write_parfile


def main():

    # User's Inputs
    rhem_version = "rhem2.4"  # options: rhem2.4, rhem2.5
    rhem_input_file = os.path.join('inputs', 'rhem_inputs.csv')

    # Look up tables
    rhem_soil_particle_lookup_table = os.path.join('inputs', 'rhem_soil_particles.csv')
    rhem_soil_texture_lookup_table = os.path.join('inputs', 'rhem_soil_texture_groups.csv')

    # Create an output folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_dir = f'outputs_{timestamp}'    
    os.makedirs(output_dir, exist_ok=True)
    
    # Read input table and convert rhem version
    df_rhem_input = pd.read_csv(rhem_input_file)
    rhem_cover_fields = ["GroundRock", "GroundLitter", "GroundBasal", "GroundCrust",
                        "FoliarSod", "FoliarBunch", "FoliarForbAnnual", "FoliarShrub"]
    df_rhem_input[rhem_cover_fields] = df_rhem_input[rhem_cover_fields] / 100
    df_rhem_input["Slope"] = df_rhem_input["Slope"] / 100
    rhem_version = rhem_version.lower()

    # Calculate RHEM parameters
    df_rhem_primary_parameters, df_rhem_particle = parameterize_rhem(df_rhem_input, rhem_version, 
                                                                     rhem_soil_texture_lookup_table, 
                                                                     rhem_soil_particle_lookup_table)

    # Write parfiles
    for plot_id in df_rhem_input.HillslopeID:
        output_file = os.path.join(output_dir, f"{plot_id}.par")
        write_parfile(output_file, rhem_version, plot_id, df_rhem_primary_parameters, df_rhem_particle)


def parameterize_rhem(df_rhem_input, rhem_version, rhem_soil_texture_lookup_table, 
                      rhem_soil_particle_lookup_table):

    if rhem_version == "rhem2.4":
        import rhem_parameterizationv2p4 as rhem
    elif rhem_version == "rhem2.5":
        import rhem_parameterizationv2p5 as rhem
    else:
        raise ValueError(f"Invalid RHEM version: {rhem_version}")
       
    print("Converting SoilTexture to RHEM Soil Texture.")
    df_rhem_input = get_rhem_texture(df_rhem_input, rhem_soil_texture_lookup_table)

    print("Calculating RHEM primary parameters.")
    df_rhem_primary_parameters = rhem.calc_rhem_primary_par(df_rhem_input)
    
    df_rhem_particle = rhem.calc_particle_properties(df_rhem_input, rhem_soil_particle_lookup_table)

    return df_rhem_primary_parameters, df_rhem_particle


def get_rhem_texture(df, rhem_soil_particle_lookup_table):

    """ Change the dominant texture to the RHEM soil texture """

    # Load lookup table
    df_texture_lookup_table = pd.read_csv(rhem_soil_particle_lookup_table)
    df_rhem_soil_texture_groups = df_texture_lookup_table[["SoilTexture", "RHEMSoilTexture"]]
    df_rhem_soil_texture_groups['SoilTexture'] = df_rhem_soil_texture_groups['SoilTexture'].str.lower()
    df_rhem_soil_texture_groups['RHEMSoilTexture'] = df_rhem_soil_texture_groups['RHEMSoilTexture'].str.lower()
    df["SoilTexture"] = df["SoilTexture"].str.lower()
    
    # Merge the two dataframes
    df_merged = pd.merge(df, df_rhem_soil_texture_groups, on="SoilTexture", how='left')
    df_merged = df_merged.drop(columns=["SoilTexture"])

    return df_merged


if __name__ == "__main__":
    main()