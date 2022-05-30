import numpy

if __name__ == "__main__":
    r = 0.04
    lon_ = numpy.arange(85.+r/2, 205, r)
    lat_ = numpy.arange(60.-r/2, -60, -r)
    print(len(lon_))
    print(lat_)