from Py6S import SixS, AtmosProfile, AeroProfile, Geometry, Wavelength, AtmosCorr
import numpy
import os

AOT = 0.0875
RAA = 32.8816
SZA = 37.8147
VZA = 70.2937
AT = 1.0
ALT = 0.0
OZ = 0.2846
WV = 1.1300

WORK_SPACE = os.getcwd()
BAND_RF_CSV = WORK_SPACE + "/AHI_AC/AHI_SF/sixs_band1.csv"
band_rf = numpy.loadtxt(BAND_RF_CSV, delimiter=",")


def atmospheric_correction_6s(band_RF, VZA, SZA, RAA, AOT, aerosol_type, ozone, water_vapour, altitude=0.):
    s = SixS()
    s.atmos_profile = AtmosProfile.UserWaterAndOzone(water_vapour, ozone)
    s.aero_profile = AeroProfile.PredefinedType(aerosol_type)
    s.aot550 = AOT
    s.wavelength = Wavelength(band_RF[0, 0], band_RF[len(band_RF) - 1, 0], band_RF[:, 1])
    s.altitudes.set_sensor_satellite_level()
    s.altitudes.set_target_custom_altitude(altitude)
    s.geometry = Geometry.User()
    s.geometry.solar_z = SZA
    s.geometry.solar_a = RAA
    s.geometry.view_z = VZA
    s.geometry.view_a = 0

    s.atmos_corr = AtmosCorr.AtmosCorrLambertianFromReflectance(0.2)
    s.run()

    # f1 = 1 / (s.outputs.transmittance_total_scattering.total * s.outputs.transmittance_global_gas.total)
    # print(f1, s.outputs.coef_xa, f1 - s.outputs.coef_xa)
    # x1 = f1
    x1 = s.outputs.coef_xa
    x2 = s.outputs.coef_xb
    x3 = s.outputs.coef_xc
    del s
    print(x1, x2, x3)
    return (x1, x2, x3)


def band_SR(xa, xb, xc, obs_r):
    y = xa * obs_r - xb
    sr = y / (1 + xc * y)
    return sr


if __name__ == "__main__":
    # AHI Observation Time
    ahi_obs_time = '201608230450'
    # roi_extent: (ullat, ullon, lrlat, lrlon)
    roi_extent = [47.325, 94.329, 47.203, 94.508]

    atmospheric_correction_6s(band_rf, VZA, SZA, RAA, AOT, AT, OZ, WV, altitude=0.)
