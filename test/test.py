if __name__ == "__main__":
    p = 3.5780965311341736e-46
    p_s = str(p).split('e')
    p_f = round(float(p_s[0][:5]), 1)
    p_str = str(p_f) + 'e' + p_s[1]