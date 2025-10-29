import multiprocessing as mp

def expand_message(que, messages):
    # the sender always calls queue.put()
    for msg in messages:
        msg = msg.replace('msg', 'message ')
        que.put(msg)
        print(f'expanded: {msg}')

    que.put(None)  # Signal the end of messages

def add_punctuation(inQue, outQue):
    while True:
        msg = inQue.get()
        if msg is None:
            outQue.put(None)  # Signal the end of messages
            break
        msg = msg + '!'
        print(f'Punctuated: {msg}')
        outQue.put(msg)

def receiver(que):
    while True:
        msg = que.get()
        if msg is None:
            break
        print(f'Received: {msg}')

if __name__ == '__main__':

    messages = ['msg1', 'msg2', 'msg3', 'msg4']

    queue = mp.Queue()
    punctuation_queue = mp.Queue()

    expander_process = mp.Process(target=expand_message, args=(queue, messages))
    punctuation_process = mp.Process(target=add_punctuation, args=(queue, punctuation_queue))
    receiving_process = mp.Process(target=receiver, args=tuple([punctuation_queue]))

    expander_process.start()
    punctuation_process.start()
    receiving_process.start()

    expander_process.join()
    punctuation_process.join()
    receiving_process.join()

