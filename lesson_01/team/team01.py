""" 
Course: CSE 351
Lesson: L01 Team Activity
File:   team.py
Author: <Add name here>
Purpose: Find prime numbers

Instructions:

- Don't include any other Python packages or modules
- Review and follow the team activity instructions (team.md)

TODO 1) Get this program running.  Get cse351 package installed
TODO 2) move the following for loop into 1 thread
TODO 3) change the program to divide the for loop into 10 threads
TODO 4) change range_count to 100007.  Does your program still work?  Can you fix it?
Question: if the number of threads and range_count was random, would your program work?
"""

from datetime import datetime, timedelta
import math
import threading
import random

# Include cse 351 common Python files
from cse351 import *

# Global variable for counting the number of primes found
prime_count = 0
numbers_processed = 0

def is_prime(n):
    """
        Primality test using 6k+-1 optimization.
        From: https://en.wikipedia.org/wiki/Primality_test
    """
    if n <= 3:
        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i ** 2 <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def do_loop(start, range_count, lock):
    global prime_count
    global numbers_processed

    for i in range(start, start + range_count):
        numbers_processed += 1
        if is_prime(i):
            with lock:
                prime_count += 1
                print(i, end=', ', flush=True)
        print(flush=True)


def main():
    global prime_count                  # Required in order to use a global variable
    global numbers_processed            # Required in order to use a global variable

    log = Log(show_terminal=True)
    log.start_timer()

    start = 10000000000
    range_count = 100000
    numbers_processed = 0

    thread_count = 10
    chunk_size = range_count/thread_count

    threads = [] #an empty array

    # processing_lock

    for i in range(1, thread_count):
        chunk_start = math.ceil(i * chunk_size)
        threads.push(threading.Thread(target=do_loop, args=(chunk_start, range_count)))
        
    for t in threads:
        t.start()

    for t in threads:
        t.join()

    # loop_doing_thread = threading.Thread(target=do_loop, args=(start, range_count))

    # loop_doing_thread.start()
    # loop_doing_thread.join()

    # Should find 4306 primes
    log.write(f'Numbers processed = {numbers_processed}')
    log.write(f'Primes found      = {prime_count}')
    log.stop_timer('Total time')


if __name__ == '__main__':
    main()
