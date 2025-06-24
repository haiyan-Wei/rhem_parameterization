import math
import numpy as np
import pandas as pd

""" Equations are from RHEM website: 
RHEM 2.2: https://apps.tucson.ars.ag.gov/rhem/assets/docs/RHEM_Equations_01222015.pdf
RHEM 2.3: https://apps.tucson.ars.ag.gov/rhem/assets/docs/RHEM_Ke_Equations_01122022.pdf
RHEM 2.4: https://apps.tucson.ars.ag.gov/rhem/assets/docs/RHEM_Kss_Equations_01122022.pdf"""


def calc_rhem_primary_par(df):

    """ Returns a dataframe with rhem parameters.
        It is okay if df has fields that are not used for this calculation. They will be carried over to output.
        Note Bare is not activated yet in RHEM"""

    df['Ke'] = df.apply(lambda row: calc_ke(row.GroundBasal, row.GroundLitter, row.FoliarShrub, 
                                            row.FoliarSod, row.FoliarBunch, row.FoliarForbAnnual, 
                                            row.RHEMSoilTexture), axis=1)

    df = calc_kss_ft_chezy_bare(df)

    df = get_rhem_default_parameters(df)

    return df


def calc_kss_ft_chezy_bare(df):
    
    df['Kss'] = df.apply(lambda row: calc_kss(row.GroundLitter, row.GroundRock, row.GroundBasal, 
                                              row.GroundCrust, row.FoliarShrub, row.FoliarSod, 
                                              row.FoliarBunch, row.FoliarForbAnnual, row.Slope), 
                                              axis=1)
               
    df['Ft'] = df.apply(lambda row: calc_ft(row.GroundLitter, row.GroundRock, row.GroundBasal, 
                                            row.GroundCrust, row.Slope), axis=1)    
    df['Chezy'] = np.sqrt(8 * 9.81 / df['Ft'])
    df['RChezy'] = df['Chezy']
    df['Bare'] = df.apply(lambda row: calc_bare(row.GroundLitter, row.GroundRock, row.GroundBasal, 
                                                row.GroundCrust), axis=1)
    
    rhem_cover_fields = ["GroundRock", "GroundLitter", "GroundBasal", "GroundCrust",
                        "FoliarSod", "FoliarBunch", "FoliarForbAnnual", "FoliarShrub"]    
    df = df.drop(columns=rhem_cover_fields)

    return df
    

def get_rhem_default_parameters(df):
    
    # Defult RHEM parameters
    KOMEGA = 0.000007747
    KCMAX = 0.000299364300
    ALF = 0.8
    ADF = 0.00
    RSP = 1.0
    SPACING = 1.0

    df['Komega'] = KOMEGA
    df['ADF'] = ADF
    df['ALF'] = ALF
    df['Kcmax'] = KCMAX
    df['RSP'] = RSP
    df['Spacing'] = SPACING

    return df
    
def calc_particle_properties(df, rhem_soil_particle_lookup_table):

    # Read in the lookup table
    df_lookup_table = pd.read_csv(rhem_soil_particle_lookup_table)

    # Rename some of the columns to match the RHEM parameters
    df_lookup_table.rename(columns={'mean_matric_potential': 'G', 
                                    'mean_porosity': 'Porosity'}, inplace=True)
    df_lookup_table['RHEMSoilTexture'] = df_lookup_table['RHEMSoilTexture'].str.lower()

    # Apply get_particle_properties once to get all properties
    particle_props = df.apply(lambda row: get_particle_properties(row.RHEMSoilTexture, df_lookup_table), axis=1)    
    
    # Assign results to new columns
    df['G'] = particle_props.apply(lambda x: x[0])
    df['Porosity'] = particle_props.apply(lambda x: x[1])
    df['Dist'] = particle_props.apply(lambda x: x[2])
    df['Smax'] = particle_props.apply(lambda x: x[3])
    df['particleFraction'] = particle_props.apply(lambda x: x[4])
    df['particleDensity'] = particle_props.apply(lambda x: x[5])
    df['diameter'] = particle_props.apply(lambda x: x[6])

    return df

    
def get_particle_properties(RHEMSoilTexture, df_lookup_table):    
           
    df_row = df_lookup_table[df_lookup_table['RHEMSoilTexture'] == RHEMSoilTexture]
    if df_row.empty:
        raise ValueError(f"Soil texture '{RHEMSoilTexture}' not found in lookup table")
    
    row = df_row.iloc[0]
    
    diameter = [
        row['clay_diameter'],
        row['silt_diameter'],
        row['small_aggregates_diameter'],
        row['large_aggregates_diameter'],
        row['sand_diameter']]
    
    particleFraction = [
        row['clay_fraction'],
        row['silt_fraction'],
        row['small_aggregates_fraction'],
        row['large_aggregates_fraction'],
        row['sand_fraction']]
    
    particleDensity = [
        row['clay_specific_gravity'],
        row['silt_specific_gravity'],
        row['small_aggregates_specific_gravity'],
        row['large_aggregates_specific_gravity'],
        row['sand_specific_gravity']]
    
    return (row['G'], row['Porosity'], row['Dist'], row['Smax'], particleFraction, particleDensity, diameter)


def calc_ft(litter, rock, basal, crypt, slope):

    ft = 10 ** (-0.109 + 1.425 * litter + 0.442 * rock 
                + 1.764*(basal + crypt) + 2.068 * slope)

    return ft


def calc_ke(basal, litter, shrub, sod, bunch, forb, rhem_soilTexture):

    cover_term = basal + litter

    if (rhem_soilTexture == 'sand'):    
       keb = 64 * (math.exp(0.3564 * cover_term))
    elif (rhem_soilTexture == 'loamy sand'):
        keb = 30.5 * (math.exp(0.3056 * cover_term))
    elif (rhem_soilTexture == 'sandy loam'):
        keb = 5 * (math.exp(1.1632 * cover_term))
    elif (rhem_soilTexture == 'loam'):
        keb = 2.5 * (math.exp(1.5686 * cover_term))
    elif (rhem_soilTexture == 'silt loam'):
        keb = 1.2 * (math.exp(2.0149 * cover_term))
    elif (rhem_soilTexture == 'silt'):
        keb = 1.2 * (math.exp(2.0149 * cover_term))
    elif (rhem_soilTexture == 'sandy clay loam'):
        keb = 0.80 * (math.exp(2.1691 * cover_term))
    elif (rhem_soilTexture == 'clay loam'):
        keb = 0.50 * (math.exp(2.3026 * cover_term))
    elif (rhem_soilTexture == 'silty clay loam'):
        keb = 0.90 * (math.exp(1.4137 * cover_term))
    elif (rhem_soilTexture == 'sandy clay'):
        keb = 0.30 * (math.exp(2.1203 * cover_term))
    elif (rhem_soilTexture == 'silty clay'):
        keb = 0.5 * (math.exp(1.2809 * cover_term))
    elif (rhem_soilTexture == 'clay'):
        keb = 0.3 * (math.exp(1.7918 * cover_term))

    keb_shrub = keb * 1.2
    keb_sod = keb * 0.8
    keb_bunch = keb * 1.0
    keb_forb = keb * 1.0

    totalFoliar = shrub + sod + bunch + forb

    ke = (keb_shrub * shrub + keb_sod * sod + keb_bunch * bunch +
          keb_forb * forb) / totalFoliar

    return ke


def calc_kss(litter, rock, basal, crypt, shrub, sod, bunch, forb, slope):

    totalFoliar = shrub + sod + bunch + forb
    ground =litter + rock + basal + crypt

    # Step 1 Calculate Kssfor each vegetation community
    if ground < 0.475:
        slope_cover_term = 2.5535 * slope - 2.547 * ground - 0.7822 * totalFoliar
        kss_bunch = 1.3 * 2.0 * 10. ** (4.154 + slope_cover_term)
        kss_sod = 1.3 * 2.0 * 10.**(4.2169 + slope_cover_term)
        kss_shrub = 1.3 * 2.0 * 10.**(4.2587 + slope_cover_term)
        kss_forb = 1.3 * 2.0 * 10.**(4.1106 + slope_cover_term)
    else:
        slope_cover_term = 2.5535 * slope - 0.4811 * ground - 0.7822 * totalFoliar
        kss_bunch = 1.3 * 2.0 * 10.**(3.1726975 + slope_cover_term)
        kss_sod = 1.3 * 2.0 * 10.**(3.2355975 + slope_cover_term)
        kss_shrub = 1.3 * 2.0 * 10.**(3.2773975 + slope_cover_term)
        kss_forb = 1.3 * 2.0 * 10.**(3.1292975 + slope_cover_term)

    # Step 2 Calculate average Kss when total foliar cover is close to 0
    if ground < 0.475:
        slope_cover_term = 2.5535 * slope - 2.547 * ground
        kss_shrub_0 = 1.3 * 2.0 * 10.**(4.2587 + slope_cover_term)
    else:
        slope_cover_term = 2.5535 * slope - 0.4811 * ground
        kss_shrub_0 = 1.3 * 2.0 * 10.**(3.2773975 + slope_cover_term)

    if (totalFoliar > 0) & (totalFoliar < 0.02):
        kss_weighted = totalFoliar/0.02 * ((shrub/totalFoliar) * kss_shrub  +
                                           (sod/totalFoliar)   * kss_sod    +
                                           (bunch/totalFoliar) * kss_bunch  +
                                           (forb/totalFoliar)  * kss_forb  +
                                           (0.02-totalFoliar)/0.02  * kss_shrub_0)    
    else:
        kss_weighted = (shrub * kss_shrub + sod * kss_sod + bunch * kss_bunch
                         + forb * kss_forb) / totalFoliar

    # Step 3 Calculate Kss used for RHEM(with canopy cover == 0 and canopy cover > 0)
    if totalFoliar == 0:
        if ground < 0.475:
            kss_rhem = 1.3 * 2.0 * 10. ** (4.2587 + 2.5535*slope - 2.547*ground)
        else:
            kss_rhem = 1.3 * 2.0 * 10. ** (3.2773975 + 2.5535*slope - 0.4811*ground)
    else:
        if ground < 0.475:
            kss_rhem = ground/0.475 * kss_weighted + (0.475 - ground)/0.475 * kss_shrub
        else:
            kss_rhem = kss_weighted

    return kss_rhem

def calc_bare(litter, rock, basal, crypt):
    return 1 - (litter + rock + basal + crypt)

