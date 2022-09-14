import matplotlib.transforms as mtransforms
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import numpy as np


def add_right_cax(ax, pad, width):

    axpos = ax.get_position()
    caxpos = mtransforms.Bbox.from_extents(axpos.x1 + pad, axpos.y0, axpos.x1 + pad + width, axpos.y1)
    cax = ax.figure.add_axes(caxpos)

    return cax


def make_fig(LC, axis_max, axis_min, X, Y, k, b, rmse, N):

    fig = plt.figure(figsize=(6, 6))
    ax1 = fig.add_subplot(111, aspect='equal')

    x = np.arange(axis_min, axis_max + 1)
    y = 1 * x

    xx = np.arange(axis_min, axis_max + 0.1, 0.05)
    yy = k * xx + b

    # Calculate the point density
    xy = np.vstack([X, Y])
    z = gaussian_kde(xy)(xy)

    # Sort the points by density, so that the densest points are plotted last
    idx = z.argsort()
    X, Y, z = X[idx], Y[idx], z[idx]
    ax1.minorticks_on()
    # x_major_locator = plt.MultipleLocator(5)
    x_minor_locator = plt.MultipleLocator(0.05)
    ax1.xaxis.set_minor_locator(x_minor_locator)
    # ax.xaxis.set_major_locator(x_major_locator)
    ax1.yaxis.set_minor_locator(x_minor_locator)
    # ax.yaxis.set_major_locator(x_major_locator)

    ax1.tick_params(axis="y", which='minor', length=5, direction='in', labelsize=15)
    ax1.tick_params(axis="y", which='major', length=10, direction='in', labelsize=15)

    ax1.tick_params(axis="x", which='minor', length=5, direction='in', labelsize=15)
    ax1.tick_params(axis="x", which='major', length=10, direction='in', labelsize=15)

    ax1.spines['right'].set_color('none')
    ax1.spines['top'].set_color('none')

    im = ax1.scatter(X, Y, marker='o', c=z, s=15, cmap='Spectral_r')

    ax1.set_xticks(np.arange(axis_min, axis_max + 0.1, 0.1))
    ax1.set_yticks(np.arange(axis_min + 0.1, axis_max + 0.1, 0.1))

    ax1.set_ylabel("AHI Ref Band4", fontsize=25)
    ax1.set_xlabel("SGLI Ref PI02", fontsize=25)

    ax1.plot(x, y, color='k', linewidth=2, linestyle='-.')
    ax1.plot(xx, yy, color='r', linewidth=2, linestyle='-')

    text_x = axis_min + (axis_max - axis_min) * 0.07
    text_y = axis_max - (axis_max - axis_min) * 0.22

    ax1.text(text_x, text_y, s='Land Cover : {}\nN = {}\nRMSE = {}\ny = {}x + {}'.format(LC, N, rmse, k, b), fontsize=18)

    cax = add_right_cax(ax1, pad=0.06, width=0.03)
    cb = fig.colorbar(im, cax=cax)
    cb.ax.set_xlabel('Count', rotation=360)
    ax1.set_xlim(axis_min, axis_max)
    ax1.set_ylim(axis_min, axis_max)
    ax1.set_title('   Surface Reflefctance\n   Inter-comparison', fontsize=25, y=1.05)
    fig.savefig('{} Band4 SR.jpg'.format(site_name), dpi=1000, bbox_inches='tight')


if __name__ == "__main__":
    site_name = ''
