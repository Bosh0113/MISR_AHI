import bz2


if __name__ == "__main__":
    ws = r'D:\Work_PhD\MISR_AHI_WS\220222'
    bz2_file = ws + '/201601112300.sun.azm.fld.4km.bin.bz2'
    zipfile = bz2.BZ2File(bz2_file)
    data = zipfile.read()
    bin_file = bz2_file[:-4]
    with open(bin_file, 'wb') as f:
        f.write(data)