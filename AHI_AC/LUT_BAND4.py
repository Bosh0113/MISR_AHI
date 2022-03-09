#!/usr/bin/env python
# coding: utf-8

import numpy as np
from Py6S import SixS, AtmosProfile, AeroProfile, Geometry, Wavelength, AtmosCorr
import time
from joblib import Parallel, delayed

sza = np.linspace(0, 80, 17)
vza = np.linspace(0, 80, 17)
water = np.linspace(0, 7, 8)
ozone = np.linspace(0.2, 0.4, 5)
AL = np.linspace(0, 4, 5)
AOT = np.array([0.01, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0])
raa = np.linspace(0, 180, 19)
# Aeropro = np.array([1,2,3,5,6])


def ac_band4(In_water, In_AOT, In_AL, In_sza, In_vza, In_raa):

    wl_band = "/data/Projects/sixs_band4.csv"
    band = np.loadtxt(wl_band, delimiter=",")

    s = SixS()
    s.atmos_profile = AtmosProfile.UserWaterAndOzone(water[In_water], 0.3)
    s.aero_profile = AeroProfile.PredefinedType(2)
    s.aot550 = AOT[In_AOT]
    s.wavelength = Wavelength(band[0, 0], band[band.shape[0] - 1, 0], band[:,
                                                                           1])
    s.altitudes.set_sensor_satellite_level()
    s.altitudes.set_target_custom_altitude(AL[In_AL])
    s.geometry = Geometry.User()
    s.geometry.solar_z = sza[In_sza]
    s.geometry.solar_a = raa[In_raa]
    s.geometry.view_z = vza[In_vza]
    s.geometry.view_a = 0

    s.atmos_corr = AtmosCorr.AtmosCorrLambertianFromReflectance(0.2)
    s.run()

    f1 = 1 / (s.outputs.transmittance_total_scattering.total *
              s.outputs.transmittance_global_gas.total)
    return (f1, s.outputs.coef_xb, s.outputs.coef_xc)
    del s


start = time.time()
AC_output = Parallel(n_jobs=32)(
    delayed(ac_band4)(In_water, In_AOT, In_AL, In_sza, In_vza, In_raa)
    for In_water in range(len(water)) for In_AOT in range(len(AOT))
    for In_AL in range(len(AL)) for In_sza in range(len(sza))
    for In_vza in range(len(vza)) for In_raa in range(len(raa)))
end = time.time()

start = time.time()
AC_output = Parallel(n_jobs=32)(
    delayed(ac_band4)(In_water, In_AOT, In_sza, In_vza, In_raa)
    for In_water in range(len(water)) for In_AOT in range(len(AOT))
    for In_sza in range(len(sza)) for In_vza in range(len(vza))
    for In_raa in range(len(raa)))
end = time.time()

T = end - start
print('time: {:.1f} secs, {:.1f} mins,{:.1f} hours'.format(
    T, T / 60, T / 3600))

X = np.array(AC_output)
X1 = X[:, 0]
X2 = X[:, 1]
X3 = X[:, 2]
outfile1 = "01_band4.csv"
outfile2 = "02_band4.csv"
outfile3 = "03_band4.csv"
np.savetxt(outfile1, X1, delimiter=',')
np.savetxt(outfile2, X2, delimiter=',')
np.savetxt(outfile3, X3, delimiter=',')
