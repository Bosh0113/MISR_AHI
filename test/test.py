import xarray
import numpy

t = 0.01

if __name__ == "__main__":
    ds = xarray.Dataset(
        data_vars={
            "v": (
                ("x", "y"),
                [[1, 4, 2, 9], [2, 7, 6, numpy.nan], [6, numpy.nan, 5, 8], [3, 2, 2, 1]],
            ),
        },
        coords={"x": [0.0, 0.75, 1.5, 2.25], "y": [3.0, 2.25, 1.5, 0.75]},
    )
    ds_xs = ds["x"]
    ds_ys = ds["y"]
    ds_xs = numpy.array(ds_xs)
    print(numpy.argmax(ds_xs==0.75))
    n_xs = numpy.arange(ds_xs[0], ds_xs[len(ds_xs)-1]+0.75, 0.01)
    n_ys = numpy.arange(ds_ys[0], ds_ys[len(ds_ys)-1]-0.75, -t)
    n_ds = ds.interp(x=n_xs, y=n_ys, method="nearest")
    # print(n_ds["v"])