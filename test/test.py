import numpy

def misr_saa_true(saa_dn):
   return (saa_dn + 180)%360

if __name__ == "__main__":
   
   # print(misr_saa_true(344.924))
   print(numpy.array([1,2,3]).mean())