import numpy


if __name__ == "__main__":
    npy_path = r'D:\Work_PhD\MISR_AHI_WS\220218\AHI_saa_ftp_paths.npy'
    ahi_saa_paths = numpy.load(npy_path)
    print(ahi_saa_paths)