import numpy
import math
import numba as nb
import time
import matplotlib.pyplot as plt

degree_step = 0.005
diff_step = 0.001

COS_diff_threshold = 0.01


@nb.jit
def is_lg_COS_diff(f_degree, s_degree):
    differ_cos = abs(math.cos(math.radians(f_degree)) - math.cos(math.radians(s_degree)))
    if differ_cos > COS_diff_threshold:
        return 1
    else:
        return 0


@nb.jit
def is_lg_COS_diff2(f_degree, s_degree):
    a1 = 0
    a2 = 0
    if f_degree > s_degree:
        a1 = f_degree
        a2 = s_degree
    else:
        a1 = s_degree
        a2 = f_degree
    differ_cos = 1 - (math.cos(math.radians(a1)) / math.cos(math.radians(a2)))
    if differ_cos > COS_diff_threshold:
        return 1
    else:
        return 0


def cos_diff_method_old():
    start = time.perf_counter()
    degree_s = numpy.arange(0., 90., 0.05)
    max_lg_diffs = numpy.zeros_like(degree_s)
    for d_index in range(len(degree_s)):
        degree_ = degree_s[d_index]
        interval = diff_step
        lg_degree = degree_ + interval
        while not is_lg_COS_diff2(degree_, lg_degree):
            interval += diff_step
            lg_degree = degree_ + interval
        max_lg_diffs[d_index] = interval

    end = time.perf_counter()
    print('Total time: ', end - start, 's')

    plt.plot(degree_s, max_lg_diffs, 'b-')
    plt.grid(which="major",
             axis="x",
             color="gray",
             alpha=0.5,
             linestyle="-",
             linewidth=0.5)
    plt.grid(which="major",
             axis="y",
             color="gray",
             alpha=0.5,
             linestyle="-",
             linewidth=0.5)
    plt.grid(which="minor",
             axis="x",
             color="gray",
             alpha=0.6,
             linestyle="--",
             linewidth=0.2)
    plt.grid(which="minor",
             axis="y",
             color="gray",
             alpha=0.6,
             linestyle="--",
             linewidth=0.2)
    ax = plt.gca()
    ax.xaxis.set_major_locator(plt.MultipleLocator(5))
    ax.xaxis.set_minor_locator(plt.MultipleLocator(1))
    ax.yaxis.set_major_locator(plt.MultipleLocator(0.5))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(0.25))
    plt.title('Max degree interval for "|cos⁡(A1)−cos⁡(A2)|≤' + str(COS_diff_threshold) + '"')
    plt.xlabel('A1 (°)')
    plt.ylabel('Max degree interval between A1 & A2 at A1 (A2>A1)')
    plt.show()


def cos_diff_method_new():
    start = time.perf_counter()
    degree_s = numpy.arange(0., 90., 0.05)
    max_lg_diffs = numpy.zeros_like(degree_s)
    for d_index in range(len(degree_s)):
        degree_ = degree_s[d_index]
        interval = diff_step
        lg_degree = degree_ + interval
        while not is_lg_COS_diff2(degree_, lg_degree):
            interval += diff_step
            lg_degree = degree_ + interval
        max_lg_diffs[d_index] = interval

    end = time.perf_counter()
    print('Total time: ', end - start, 's')

    plt.plot(degree_s, max_lg_diffs, 'b-')
    plt.grid(which="major",
             axis="x",
             color="gray",
             alpha=0.5,
             linestyle="-",
             linewidth=0.5)
    plt.grid(which="major",
             axis="y",
             color="gray",
             alpha=0.5,
             linestyle="-",
             linewidth=0.5)
    plt.grid(which="minor",
             axis="x",
             color="gray",
             alpha=0.6,
             linestyle="--",
             linewidth=0.2)
    plt.grid(which="minor",
             axis="y",
             color="gray",
             alpha=0.6,
             linestyle="--",
             linewidth=0.2)
    ax = plt.gca()
    ax.xaxis.set_major_locator(plt.MultipleLocator(5))
    ax.xaxis.set_minor_locator(plt.MultipleLocator(1))
    ax.yaxis.set_major_locator(plt.MultipleLocator(0.5))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(0.25))
    plt.title('Max degree interval for "1-cos⁡(A2)/cos⁡(A1)≤' + str(COS_diff_threshold) + '"')
    plt.xlabel('A1 (°)')
    plt.ylabel('Max degree interval between A1 & A2 at A1 (A2>A1)')
    plt.show()


if __name__ == "__main__":
    # cos_diff_method_old()
    cos_diff_method_new()
