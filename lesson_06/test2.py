import multiprocessing as mp

def sender(conn, msg):
    for m in msg:
        conn.send(m)
    conn.send(None)
    conn.close()

def receiver(conn):
    while True:
        m = conn.recv()
        if m is None:
            break
        print("Received:", m)
    conn.close()

if __name__ == '__main__':

    msgs = ['hi','hello','howdy','heyas']

    myPipe = mp.Pipe()

    parent_conn, child_conn = myPipe

    parentProcess = mp.Process(target=sender, args=(parent_conn, msgs))
    childProcess = mp.Process(target=receiver, args=(child_conn,))

    parentProcess.start()
    childProcess.start()

    parentProcess.join()
    childProcess.join()

