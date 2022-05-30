import xarray
import numpy
import matplotlib.pyplot as plt

t = 0.01
r = 0.75

if __name__ == "__main__":
    value = [[1, 4, 2, 9], [2, 7, 6, 1], [6, 3, 5, 8], [3, 2, 2, 1]]
    plt.imshow(value)
    plt.show()
    ds = xarray.Dataset(
        data_vars={
            "v": (
                ("x", "y"),
                value,
            ),
        },
        coords={"x": [0.0, 0.75, 1.5, 2.25], "y": [3.0, 2.25, 1.5, 0.75]},
    )
    ds_xs = ds["x"]
    ds_ys = ds["y"]
    ds_xs = numpy.array(ds_xs)
    n_xs = numpy.arange(ds_xs[0]-r/2, ds_xs[len(ds_xs)-1] + r/2, t)
    n_ys = numpy.arange(ds_ys[0]+r/2, ds_ys[len(ds_ys)-1] - r/2, -t)
    n_ds = ds.interp(x=n_xs, y=n_ys, method="nearest", kwargs={"fill_value": "extrapolate"})
    plt.imshow(n_ds["v"])
    plt.show()
    # print(n_ds["v"])