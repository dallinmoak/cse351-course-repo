import multiprocessing as mp

def f(n,a):
    # changing doouble value
    n.value = 3.14159

    # changing array values
    for i in range(len(a)):
        a[i] = -a[i]

if __name__ == '__main__':

    num = mp.Value('d', 0.0)
    arr = mp.Array('i', range(10))
    p = mp.Process(target=f, args=(num, arr))
    p.start()
    p.join()

    print(num.value)
    print(arr)
    print(list(arr))  # Convert to list for easier readability