import numpy

if __name__ == "__main__":
    array = [0, 12, 1, 3, 2]
    array1 = [0.0]
    array = numpy.array(array)
    b_a = array[numpy.isin(array, array1)]
    print(b_a)