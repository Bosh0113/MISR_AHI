from Py6S import SixS, AtmosProfile, AeroProfile, Geometry, Wavelength, AtmosCorr
import numpy
import os

VZA = 70.57832
SZA = 67.64781
RAA = 22.20868
AOT = 0.02187729        # JAXA
# AOT = 0.03416528553     # CAMS
AT = 1.0
ALT = 0.55
OZ = 0.3509108
WV = 0.3950571

AHI_TOA = 0.20294118

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

    f1 = 1 / (s.outputs.transmittance_total_scattering.total * s.outputs.transmittance_global_gas.total)
    x1 = s.outputs.coef_xa
    x2 = s.outputs.coef_xb
    x3 = s.outputs.coef_xc
    del s
    return f1, x1, x2, x3


def band_SR(xa, xb, xc, obs_r):
    y = xa * obs_r - xb
    sr = y / (1 + xc * y)
    return sr


if __name__ == "__main__":
    f1, x1, x2, x3 = atmospheric_correction_6s(band_rf, VZA, SZA, RAA, AOT, AT, OZ, WV, ALT)
    print('f1, x1, x2, x3:', f1, x1, x2, x3)
    print(AHI_TOA)
    AHI_SR = band_SR(f1, x2, x3, AHI_TOA)
    print(AHI_SR)
