from multiprocessing import Pool

def f(x):
    return x*x

if __name__ == '__main__':
    p = Pool(8)
    print(p.map(f, [1, 2, 3]))