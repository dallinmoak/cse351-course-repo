"""
Course: CSE 351
Lesson: L02 team activity
File:   team.py
Author: <Add name here>

Purpose: Retrieve Star Wars details from a server

Instructions:

- This program requires that the server.py program be started in a terminal window.
- The program will retrieve the names of:
    - characters
    - planets
    - starships
    - vehicles
    - species

- the server will delay the request by 0.5 seconds

TODO
- Create a threaded class to make a call to the server where
  it retrieves data based on a URL.  The class should have a method
  called get_name() that returns the name of the character, planet, etc...
- The threaded class should only retrieve one URL.

- Speed up this program as fast as you can by:
    - creating as many as you can
    - start them all
    - join them all

"""

from asyncio import threads
from datetime import datetime, timedelta
import threading

from common import *

# Include cse 351 common Python files
from cse351 import *

# global
call_count = 0

# def get_urls(film6, kind):
#     global call_count

#     urls = film6[kind]
#     print(kind)
#     for url in urls:
#         call_count += 1
#         item = get_data_from_server(url)
#         print(f'  - {item['name']}')


class FetcherThread(threading.Thread):
    def __init__(self, url, call_count_lock):
        threading.Thread.__init__(self)
        self.url = url['url']
        self.kind = url['kind']
        self.call_count_lock = call_count_lock

    def get_data(self):
        full_data = self.data
        full_data = dict(self.data)
        full_data['kind'] = self.kind
        return full_data

    def run(self):
        global call_count
        with self.call_count_lock:
            call_count += 1
        self.data = get_data_from_server(self.url)
        # print(f"  - {self.data['name']}")


def main():
    global call_count

    global my_results

    my_results = {}

    call_count_lock: threading.Lock = threading.Lock()

    log = Log(show_terminal=True)
    log.start_timer("Starting to retrieve data from the server")

    film6 = get_data_from_server(f"{TOP_API_URL}/films/6")
    call_count += 1
    print_dict(film6)

    data_type = ["characters", "planets", "starships", "vehicles", "species"]

    all_Urls = []
    threads = []

    for kind in data_type:
        urls = film6[kind]
        for url in urls:
            all_Urls.append({'url': url, 'kind': kind})

    for url in all_Urls:
        thread = FetcherThread(url, call_count_lock)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    for thread in threads:
        item = thread.get_data()
        kind = item['kind']
        if kind not in my_results:
            my_results[kind] = []
        my_results[kind].append(item)

    print_dict(my_results)


    log.stop_timer("Total Time To complete")
    log.write(f"There were {call_count} calls to the server")


if __name__ == "__main__":
    main()
