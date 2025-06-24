import math
from rhem_parameterizationv2p4 import calc_kss_ft_chezy_bare, get_rhem_default_parameters, calc_particle_properties
                                       

"""Equations are not on RHEM website yet. Only Ke equations are changed in RHEM v2.5 """

def calc_rhem_primary_par(df):

    """ Only Ke equations are changed in RHEM v2.5 """

    df['Ke'] = df.apply(lambda row: calc_ke2p5(row.GroundBasal, row.GroundLitter, row.FoliarShrub,
                                            row.FoliarSod, row.FoliarBunch, row.FoliarForbAnnual, 
                                            row.RHEMSoilTexture), axis=1)
    
    df = calc_kss_ft_chezy_bare(df)

    df = get_rhem_default_parameters(df)
    
    return df


def calc_ke2p5(basal, litter, shrub, sod, bunch, forb, rhem_soilTexture):

    ground_cover = basal + litter
    foliar_cover = shrub + sod + bunch + forb    
    
    cover_term = 1.81 * ground_cover + 1.059 * foliar_cover
    if (rhem_soilTexture == 'sand'):    
        keb = 2.40 * math.exp(cover_term)
    elif (rhem_soilTexture == 'loamy sand'):
        keb = 2.20 * math.exp(cover_term)
    elif (rhem_soilTexture == 'sandy loam'):
        keb = 1.90 * math.exp(cover_term)
    elif (rhem_soilTexture == 'loam'):
        keb = 1.40 * math.exp(cover_term)        
    elif (rhem_soilTexture == 'silt loam'):
        keb = 1.70 * math.exp(cover_term)
    elif (rhem_soilTexture == 'silt'):
        keb = 2.25 * math.exp(cover_term)
    elif (rhem_soilTexture == 'sandy clay loam'):
        keb = 1.13 * math.exp(cover_term)
    elif (rhem_soilTexture == 'clay loam'):
        keb = 0.90 * math.exp(cover_term)
    elif (rhem_soilTexture == 'silty clay loam'):
        keb = 0.93 * math.exp(cover_term)
    elif (rhem_soilTexture == 'sandy clay'):
        keb = 0.72 * math.exp(cover_term)
    elif (rhem_soilTexture == 'silty clay'):
        keb = 0.61 * math.exp(cover_term)
    elif (rhem_soilTexture == 'clay'):
        keb = 0.37 * math.exp(cover_term)

    keb_shrub = keb * 1.2
    keb_sod = keb * 0.8
    keb_bunch = keb * 1.0
    keb_forb = keb * 1.0

    ke = (keb_shrub * shrub + keb_sod * sod + keb_bunch * bunch +
          keb_forb * forb) / foliar_cover

    return ke

