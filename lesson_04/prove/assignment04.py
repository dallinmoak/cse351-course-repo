"""
Course    : CSE 351
Assignment: 04
Student   : <your name here>

Instructions:
    - review instructions in the course

In order to retrieve a weather record from the server, Use the URL:

f'{TOP_API_URL}/record/{name}/{recno}

where:

name: name of the city
recno: record number starting from 0

"""

import time
from common import *
from threading import Thread
from queue import Queue

from cse351 import *

THREADS = 100  # TODO - set for your program
WORKERS = 10
RECORDS_TO_RETRIEVE = 5000  # Don't change


# ---------------------------------------------------------------------------
def retrieve_weather_data(
    fetcher_queue: Queue[tuple[str, int] | None],
    worker_queue: Queue[tuple[str, float, str]],
):
    while True:
        name, recno = fetcher_queue.get()
        if name is None:
            break
        print(f"retrieving record {recno} for {name}...")
        res = get_data_from_server(f"{TOP_API_URL}/record/{name}/{recno}")
        worker_queue.put((name, res["temp"], res["date"]))


# ---------------------------------------------------------------------------
def verify_noaa_results(noaa):

    answers = {
        "sandiego": 14.5004,
        "philadelphia": 14.865,
        "san_antonio": 14.638,
        "san_jose": 14.5756,
        "new_york": 14.6472,
        "houston": 14.591,
        "dallas": 14.835,
        "chicago": 14.6584,
        "los_angeles": 15.2346,
        "phoenix": 12.4404,
    }

    print()
    print("NOAA Results: Verifying Results")
    print("===================================")
    for name in CITIES:
        answer = answers[name]
        avg = noaa.get_temp_details(name)

        if abs(avg - answer) > 0.00001:
            msg = f"FAILED  Expected {answer}"
        else:
            msg = f"PASSED"
        print(f"{name:>15}: {avg:<10} {msg}")
    print("===================================")

# ---------------------------------------------------------------------------
# TODO - Complete this class
class NOAA:

    def __init__(self):
        self.data = {}

    def get_temp_details(self, city):
        print(f'computing avg for {city}...')
        total = 0.0
        count = 0
        for rec in self.data[city]:
            total += rec[1]
            count += 1
        avg = total / count
        print('finished computing avg')
        return avg

    def addRecord(self, dataPoint: tuple[str, float, str]):
        name, temp, date = dataPoint
        if name not in self.data:
            self.data[name] = []
        self.data[name].append((date, temp))

# ---------------------------------------------------------------------------
class Worker(Thread):
    def __init__(
        self,
        worker_queue: Queue[tuple[str, float, str] | None],
        noaa: NOAA,
    ):
        super().__init__()
        self.worker_queue = worker_queue
        self.noaa = noaa

    def run(self):
        while True:
            item = self.worker_queue.get()
            if item is None:
                break
            self.noaa.addRecord(item)

# ---------------------------------------------------------------------------
def main():

    log = Log(show_terminal=True, filename_log="assignment.log")
    log.start_timer()

    noaa = NOAA()

    # Start server
    data = get_data_from_server(f"{TOP_API_URL}/start")

    # Get all cities number of records
    print("Retrieving city details")
    city_details = {}
    name = "City"
    print(f"{name:>15}: Records")
    print("===================================")
    for name in CITIES:
        city_details[name] = get_data_from_server(f"{TOP_API_URL}/city/{name}")
        print(f"{name:>15}: Records = {city_details[name]['records']:,}")
    print("===================================")

    records = RECORDS_TO_RETRIEVE

    # TODO - Create any queues, pipes, locks, barriers you need

    fetching_queue: Queue[tuple[str, int] | None] = Queue()

    for name in CITIES:
        for recno in range(records):
            fetching_queue.put((name, recno))

    fetchers: list[Thread] = []

    worker_queue: Queue[tuple[str, float, str] | None] = Queue()

    for _ in range(THREADS):
        thread = Thread(
            target=retrieve_weather_data,
            args=(fetching_queue, worker_queue),
        )
        fetchers.append(thread)
        thread.start()


    workers: list[Worker] = []

    for _ in range(WORKERS):
        worker = Worker(worker_queue, noaa)
        workers.append(worker)
        worker.start()

    for _ in fetchers:
        fetching_queue.put(None)
    for fetcher in fetchers:
        fetcher.join()
    for _ in workers:
        worker_queue.put(None)
    for worker in workers:
        worker.join()

    # End server - don't change below
    data = get_data_from_server(f"{TOP_API_URL}/end")
    print(data)

    verify_noaa_results(noaa)

    log.stop_timer("Run time: ")


if __name__ == "__main__":
    main()
