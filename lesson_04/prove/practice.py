import threading
from queue import Queue
import requests
import time

# ----- Producer threads: fetchers -----
def fetcher(input_q, mid_q):
    while True:
        item = input_q.get()
        if item is None:
            mid_q.put(None)
            break
        try:
            r = requests.get(f"http://localhost:8080/{item}")
            # print(f"Fetched item {item}")
            mid_q.put(r.json())
        except Exception as e:
            mid_q.put({"item": item, "error": str(e)})

# ----- Consumer threads: processors -----
class Processor(threading.Thread):
    def __init__(self, mid_q, output_list):
        super().__init__()
        self.mid_q = mid_q
        self.output_list = output_list

    def run(self):
        while True:
            data = self.mid_q.get()
            if data is None:
                break
            # pretend processing
            result = int(data["item"]) * 2
            self.output_list.append(result)

# ----- Main control -----
def main():
    n_items = 50000
    n_fetchers = 1500
    n_processors = 20

    q_in = Queue()
    q_mid = Queue()
    results = []

    # populate input queue
    for i in range(n_items):
        q_in.put(i)

    # start fetchers
    fetchers = [threading.Thread(target=fetcher, args=(q_in, q_mid)) for _ in range(n_fetchers)]
    for f in fetchers:
        f.start()

    # start processors
    processors = [Processor(q_mid, results) for _ in range(n_processors)]
    for p in processors:
        p.start()

    # stop signals
    for _ in fetchers:
        q_in.put(None)
    for f in fetchers:
        f.join()

    for _ in processors:
        q_mid.put(None)
    for p in processors:
        p.join()

    return {
        "processed": n_items,
        "fetchers": n_fetchers,
        "processors": n_processors,
    }

if __name__ == "__main__":
    start = time.time()
    data = main()
    count = data["processed"]
    fetchers = data["fetchers"]
    processors = data["processors"]
    print(f"Fetchers: {fetchers}, Processors: {processors}")
    print("Elapsed:", round(time.time() - start, 2), "seconds")
    print("Processed items:", count)
    print("Throughput:", round(count / (time.time() - start), 2), "items/second")
