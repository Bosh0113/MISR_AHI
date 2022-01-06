import numpy
import matplotlib.pyplot as plt
# import global_land_mask as globe


# def AHI_pixel_is_land(x_index, y_index, m_size=3000):
#     offset = 120. / m_size
#     lon = 85. + (offset * (x_index + 1 / 2))
#     if lon > 180:
#         lon = lon - 360.
#     lat = 60. - offset * (y_index + 1 / 2)
#     return globe.is_land(lat, lon)


def x2dgree(x_index, y_index, m_size=3000):
    offset = 120. / m_size
    lon = 85. + (offset * (x_index + 1 / 2))
    if lon > 180:
        lon = lon - 360.
    lat = 60. - offset * (y_index + 1 / 2)
    return lat, lon


if __name__ == "__main__":
    a = numpy.zeros((3000, 3000))
    lats = []
    lons = []
    for i in range(len(a)):
        for j in range(len(a[0])):
            lat, lon = x2dgree(j, i)
            lats.append(lat)
            lons.append(lon)
    lats = numpy.array(lats)
    lats = lats.reshape(3000, 3000)
    lons = numpy.array(lons)
    lons = lons.reshape(3000, 3000)
    plt.imshow(lats)
    plt.colorbar()
    plt.show()
    plt.imshow(lons)
    plt.colorbar()
    plt.show()
