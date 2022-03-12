#!/usr/bin/env python
# coding: utf-8

import numpy as np
from Py6S import SixS, AtmosProfile, AeroProfile, Geometry, Wavelength, AtmosCorr
import time
from joblib import Parallel, delayed

# water = np.linspace(0, 7, 8)
Ozone = np.linspace(0.2, 0.4, 5)
# AL = np.linspace(0,4,5)
AOT = np.array([0.01, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0])
SZA = np.linspace(0, 80, 17)
VZA = np.linspace(0, 80, 17)
RAA = np.linspace(0, 180, 19)
# Aeropro = np.array([1,2,3,5,6])


def ac_band1(In_Ozone, In_AOT, In_SZA, In_VZA, In_RAA):

    wl_band = "./AHI_SF/sixs_band1.csv"
    band = np.loadtxt(wl_band, delimiter=",")
    
    s = SixS()
    s.atmos_profile = AtmosProfile.UserWaterAndOzone(3, In_Ozone)
    s.aero_profile = AeroProfile.PredefinedType(2)  # AeroProfile.Maritime
    s.aot550 = In_AOT
    s.wavelength = Wavelength(band[0, 0], band[len(band) - 1, 0], band[:, 1])
    s.altitudes.set_sensor_satellite_level()
    s.altitudes.set_target_custom_altitude(0)
    s.geometry = Geometry.User()
    s.geometry.solar_z = In_SZA
    s.geometry.solar_a = In_RAA
    s.geometry.view_z = In_VZA
    s.geometry.view_a = 0

    s.atmos_corr = AtmosCorr.AtmosCorrLambertianFromReflectance(0.2)
    s.run()

    f1 = 1 / (s.outputs.transmittance_total_scattering.total *
              s.outputs.transmittance_global_gas.total)
    return (f1, s.outputs.coef_xb, s.outputs.coef_xc)
    del s


start = time.time()
AC_output = Parallel(n_jobs=32)(
    delayed(ac_band1)(In_Ozone, In_AOT, In_SZA, In_VZA, In_RAA)
    for In_Ozone in Ozone for In_AOT in AOT for In_SZA in SZA for In_VZA in VZA
    for In_RAA in RAA)
end = time.time()

T = end - start
print('time: {:.1f} secs, {:.1f} mins,{:.1f} hours'.format(
    T, T / 60, T / 3600))

X = np.array(AC_output)
X1 = X[:, 0]
X2 = X[:, 1]
X3 = X[:, 2]
outfile1 = "01_band1.csv"
outfile2 = "02_band1.csv"
outfile3 = "03_band1.csv"
np.savetxt(outfile1, X1, delimiter=',')
np.savetxt(outfile2, X2, delimiter=',')
np.savetxt(outfile3, X3, delimiter=',')
