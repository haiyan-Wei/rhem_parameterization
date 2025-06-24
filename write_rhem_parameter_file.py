import os
from datetime import datetime


def write_parfile(output_file, rhem_version, plot_id, df_rhem_parameters, df_rhem_particle):


    if rhem_version == "rhem2.4" or rhem_version == "rhem2.5":
        diams_line = "   DIAMS   =   0.002000 0.010000 0.030000 0.300000 0.200000 ! mm\n"
        density_line = "   DENSITY =   2.600000 2.650000 1.800000 1.600000 2.650000 ! g/cc\n"
        
    file_info = (f"! Parameter file for scenario:\n"
                 f"!  RHEM Version:                         {rhem_version}\n"
                 f"!  File Created:                        {datetime.now():%Y-%m-%d %H:%M:%S}\n"
                 f"!  Plot ID:                              {plot_id}\n"
                 f"! End of File Info\n\n")

    global_info = ("BEGIN GLOBAL\n"
                   "   CLEN = 125.0\n"
                   "   UNITS = METRIC\n"
                   f"{diams_line}"
                   f"{density_line}"
                   f"   TEMP = 40                 ! deg C\n"
                   f"   NELE = 1\n"
                   "END GLOBAL\n\n")
    
    print(f"Writing parameter file for plot {plot_id}")
    output_directory = os.path.split(output_file)[0]
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    f = open(output_file, "w")
    f.write(file_info)
    f.write(global_info)
    f.write(write_rhem_single_hillslope(plot_id, df_rhem_parameters, df_rhem_particle))
    f.close()



def write_rhem_single_hillslope(plot_id, df_rhem_parameters, df_rhem_particle):

    primiary_parameters = df_rhem_parameters[df_rhem_parameters.HillslopeID==plot_id].squeeze()
    particle_parameters = df_rhem_particle[df_rhem_particle.HillslopeID==plot_id].squeeze()

    length =  primiary_parameters.SlopeLength
    slope = primiary_parameters.Slope

    g = particle_parameters.G
    dist, por = particle_parameters.Dist, particle_parameters.Porosity
    smax = particle_parameters.Smax
    rock = particle_parameters.GroundRock

    # order of particles: clay, silt, small_agg, large_agg, sand
    clay_fraction = particle_parameters.particleFraction[0]
    silt_fraction = particle_parameters.particleFraction[1]
    small_agg_fraction = particle_parameters.particleFraction[2]
    large_agg_fraction = particle_parameters.particleFraction[3]
    sand_fraction = particle_parameters.particleFraction[4]    

    bare = primiary_parameters.Bare
    chezy = primiary_parameters.Chezy
    rchezy = primiary_parameters.RChezy
    ke = primiary_parameters.Ke
    kss = primiary_parameters.Kss    
    komega = primiary_parameters.Komega
    adf = primiary_parameters.ADF
    alf = primiary_parameters.ALF
    kcmax = primiary_parameters.Kcmax
    rsp = primiary_parameters.RSP
    spacing = primiary_parameters.Spacing   

    plane_info = ("BEGIN PLANE\n"
                    f"  ID = 1\n"
                    f"  LEN = {length:.4f}\n"
                    f"  WIDTH = 1.0\n"
                    f"  CHEZY = {chezy:.16f}\n"
                    f"  RCHEZY = {rchezy:.16f}\n"
                    f"  SL = {slope:.4f}, {slope:.4f}\n"
                    f"  SX = 0.00000, 1.0000\n"
                    f"  CV = 1.0\n"
                    f"  SAT = 0.25\n"
                    f"  PR = 1\n"
                    f"  KSS = {kss:.16f}\n"
                    f"  KOMEGA = {komega:.9f}\n"
                    f"  KCM = {kcmax:.10f}\n"
                    f"  CA = 1.0\n"
                    f"  IN = 0.0\n"
                    f"  KE = {ke:.16f}\n"
                    f"  G = {g:.4f}\n"
                    f"  DIST = {dist:.4f}\n"
                    f"  POR = {por:.4f}\n"
                    f"  ROCK = {rock:.4f}\n"
                    f"  SMAX = {smax:.4f}\n"
                    f"  ADF = {adf:.1f}\n"
                    f"  ALF = {alf:.1f}\n"
                    f"  BARE = {bare:.4f}   ! INACTIVE\n"
                    f"  RSP = {rsp:.1f}\n"
                    f"  SPACING = {spacing:.1f}\n"
                    f"  FRACT = {clay_fraction:.4f} {silt_fraction:.4f} {small_agg_fraction:.4f} {large_agg_fraction:.4f} {sand_fraction:.4f}\n"
                    "END PLANE\n")

    return plane_info

