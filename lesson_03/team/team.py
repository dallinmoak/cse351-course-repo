"""
Course: CSE 351 
Lesson: L03 team activity
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
- Create a threaded function to make a call to the server where
  it retrieves data based on a URL.  The function should have a method
  called get_name() that returns the name of the character, planet, etc...
- The threaded function should only retrieve one URL.
- Create a queue that will be used between the main thread and the threaded functions

- Speed up this program as fast as you can by:
    - creating as many as you can
    - start them all
    - join them all

"""

from datetime import datetime, timedelta
import threading
from common import *

# Include cse 351 common Python files
from cse351 import *
import json

# global
call_count = 0

class FilmGetter(threading.Thread):
    def __init__(self, film_no, call_count_lock):
        threading.Thread.__init__(self)
        self.url = f'{TOP_API_URL}/films/{film_no}'
        self.film_data = None
        self.call_count_lock = call_count_lock

    def run(self):
        global call_count
        self.film_data = get_data_from_server(self.url)
        with self.call_count_lock:
            call_count += 1

    def get_film_data(self):
        return self.film_data

class ItemGetter(threading.Thread):
    def __init__(self, item: tuple[str, str], url, call_count_lock):
        threading.Thread.__init__(self)
        # item is expected to be (kind, url)
        self.url = url
        self.kind = item[0]
        self.film_no = item[1]
        self.item_data = None
        self.call_count_lock = call_count_lock

    def run(self):
        global call_count
        self.item_data = get_data_from_server(self.url)
        with self.call_count_lock:
            call_count += 1

    def get_item_data(self):
        return {
            'kind': self.kind,
            'film_no': self.film_no,
            'data': self.item_data
        }

def main():
    global call_count

    call_count_lock = threading.Lock()

    log = Log(show_terminal=True)
    log.start_timer('Starting to retrieve data from the server')

    film_getters = []

    for i in range(6):
        filmNo = i + 1
        film_getter = FilmGetter(filmNo, call_count_lock)
        film_getters.append(film_getter)
        film_getter.start()

    film_data = {}

    for getter in film_getters:
        getter.join()
        film_data[getter.get_film_data()['episode_id']] = getter.get_film_data()

    item_types = ['characters', 'planets', 'starships', 'vehicles', 'species']

    item_getters = []

    for key in sorted(film_data.keys()):
        for item_type in item_types:
            urls = film_data[key][item_type]
            for url in urls:
                item_info = (item_type, key)
                item_getter = ItemGetter(item_info, url, call_count_lock)
                item_getters.append(item_getter)
                item_getter.start()

    for getter in item_getters:
        getter.join()
        item_data = getter.get_item_data()
        print(f"{item_data['kind'].capitalize()} from Episode {item_data['film_no']}: {item_data['data']['name']}")
        

    log.stop_timer('Total Time To complete')
    log.write(f'There were {call_count} calls to the server')

if __name__ == "__main__":
    main()
