
import numpy
import matplotlib.pyplot as plt

AHI_AC_npy = r'D:\Work_PhD\MISR_AHI_WS\220614\202102282140_ac_band4.npy'


ac_info = numpy.load(AHI_AC_npy, allow_pickle=True)[0]
roi_ahi_sr = ac_info['roi_ahi_sr']
print(roi_ahi_sr.shape)
plt.imshow(roi_ahi_sr)
plt.colorbar()
plt.show()