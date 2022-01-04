import numpy


if __name__ == "__main__":
    aa = [2, 2, 5, 7, 8, 2, 3, 11, 5, 10]
    aa = numpy.array(aa)
    aa[((aa > 8)|(aa < 3))|(aa==5)] = -1
    print(aa)