#!/usr/bin/env python
# coding: utf-8
import os
import numpy as np
from Py6S import SixS, AtmosProfile, AeroProfile, Geometry, Wavelength, AtmosCorr
import time

WORK_SPACE = os.getcwd()

# water = 4
Ozone = 0.25
# AL = 1
AOT = 0.1
SZA = 45
VZA = 45
RAA = 90
# Aeropro = 3


def ac_band1(In_Ozone, In_AOT, In_SZA, In_VZA, In_RAA):
    wl_band = WORK_SPACE + "/AHI_AC/AHI_SF/sixs_band1.csv"
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

    f1 = 1 / (s.outputs.transmittance_total_scattering.total * s.outputs.transmittance_global_gas.total)
    return (f1, s.outputs.coef_xb, s.outputs.coef_xc)
    del s


if __name__ == "__main__":
    start = time.time()

    AC_output = ac_band1(Ozone, AOT, SZA, VZA, RAA)
    print(AC_output)

    end = time.time()
    T = end - start
    print('time: {:.1f} secs, {:.1f} mins, {:.1f} hours'.format(T, T / 60, T / 3600))
