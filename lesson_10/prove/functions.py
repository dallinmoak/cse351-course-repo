"""
Course: CSE 351, week 10
File: functions.py
Author: Dallin Moak

Instructions:

Depth First Search
https://www.youtube.com/watch?v=9RHO6jU--GU

Breadth First Search
https://www.youtube.com/watch?v=86g8jAQug04


Requesting a family from the server:
family_id = 6128784944
data = get_data_from_server('{TOP_API_URL}/family/{family_id}')

Example JSON returned from the server
{
    'id': 6128784944,
    'husband_id': 2367673859,        # use with the Person API
    'wife_id': 2373686152,           # use with the Person API
    'children': [2380738417, 2185423094, 2192483455]    # use with the Person API
}

Requesting an individual from the server:
person_id = 2373686152
data = get_data_from_server('{TOP_API_URL}/person/{person_id}')

Example JSON returned from the server
{
    'id': 2373686152,
    'name': 'Stella',
    'birth': '9-3-1846',
    'parent_id': 5428641880,   # use with the Family API
    'family_id': 6128784944    # use with the Family API
}


--------------------------------------------------------------------------------------
You will lose 10% if you don't detail your part 1 and part 2 code below

Describe how to speed up part 1

    The very first thing I did was make some helper functions to make person & family retreivial less verbose. after that, I did a recursive pattern with no threads by just starting a new recursion on each parent. I tried it with 2 and 3 gens and it was giving between 3 and 4 records per second.

    I started by spinning off a thread for each recursion. This resulted in some speedup, but it was still > 15 secs for 6 gens. Then I remembered what B. Comeau said in class about why not parallelize all calls to the server (a person call is a person call). I implemented this by just making a bunch of threads for each person that needs to be retreived per family. That got me down to 3-4 seconds for 6 gens.


Describe how to speed up part 2

    I created a List of family ids to process, seeded that list with an ID, and then made a loop that processes the current family and adds both parents to the queue list. this took 30+ seconds for 6 gens. 

    after that I made a thread function for each loop iteration. This resulted in a speedup but the queue was only receiving 1 generation at a time.

Extra (Optional) 10% Bonus to speed up part 3

<Add your comments here>

"""

from common import *
import queue
from threading import Thread, Lock


def gp(id: str) -> Person:
    """Get a person from the server and return a Person object"""
    data = get_data_from_server(f"{TOP_API_URL}/person/{id}")
    # print(f"Person data retrieved: {data}")
    return Person(data)


def gf(id: str) -> Family:
    """Get a family from the server and return a Family object"""
    data = get_data_from_server(f"{TOP_API_URL}/family/{id}")
    # print(f"Family data retrieved: {data}")
    return Family(data)


def add_person_id(person_id: str, tree: Tree) -> Person:
    """Add a person to the tree by their ID and return the Person object"""
    if tree.does_person_exist(person_id):
        return tree.get_person(person_id)
    person = gp(person_id)
    tree.add_person(person)
    # print(f"Added person {person.get_name()} with ID {person.get_id()} to the tree")
    return person


def add_family_id(family_id: str, tree: Tree) -> Family:
    """Add a family to the tree by their ID and return the Family object"""
    family = gf(family_id)
    if not tree.does_family_exist(family.get_id()):
        tree.add_family(family)
    # print(f"Added family with ID {family.get_id()} to the tree")
    return family


# -----------------------------------------------------------------------------
def depth_fs_pedigree(family_id: str, tree: Tree):
    # this is supposed to be recursive, can't do inner function recursion here, tho..

    current_fam = add_family_id(family_id, tree)

    ids_to_process = []

    ids_to_process.append(current_fam.get_husband())
    ids_to_process.append(current_fam.get_wife())
    for child_id in current_fam.get_children():
        ids_to_process.append(child_id)

    person_threads = []
    for person_id in ids_to_process:
        if person_id is not None:
            tr = Thread(target=add_person_id, args=(person_id, tree))
            person_threads.append(tr)
            tr.start()

    for tr in person_threads:
        tr.join()

    parent_fam_ids = []
    husband = tree.get_person(current_fam.get_husband())
    wife = tree.get_person(current_fam.get_wife())
    if husband.get_parentid() is not None:
        parent_fam_ids.append(husband.get_parentid())
    if wife.get_parentid() is not None:
        parent_fam_ids.append(wife.get_parentid())

    threads = []
    for parent_fam_id in parent_fam_ids:
        tr = Thread(target=depth_fs_pedigree, args=(parent_fam_id, tree))
        threads.append(tr)
        tr.start()

    for tr in threads:
        tr.join()

    return tree


# -----------------------------------------------------------------------------
def breadth_fs_pedigree(family_id, tree: Tree):
    # not recursive, but dumping records into a queue and processing them in order fifo
    # " use a list for the queue; aka DON"T use a queue.Queue() but just []"

    global fam_queue
    fam_queue = []

    fam_queue.append(family_id)

    def process_family(family_id, tree):

        global fam_queue

        fam = add_family_id(family_id, tree)
        ids_to_process = []

        ids_to_process.append(fam.get_husband())
        ids_to_process.append(fam.get_wife())
        for child_id in fam.get_children():
            ids_to_process.append(child_id)

        person_threads = []
        for person_id in ids_to_process:
            if person_id is not None:
                tr = Thread(target=add_person_id, args=(person_id, tree))
                person_threads.append(tr)
                tr.start()

        for tr in person_threads:
            tr.join()

        husband = tree.get_person(fam.get_husband())
        wife = tree.get_person(fam.get_wife())
        if husband.get_parentid() is not None:
            fam_queue.append(husband.get_parentid())
        if wife.get_parentid() is not None:
            fam_queue.append(wife.get_parentid())

    loop_threads = []

    while len(fam_queue) > 0:
        current_fam_id = fam_queue.pop(0)
        tr = Thread(target=process_family, args=(current_fam_id, tree))
        loop_threads.append(tr)
        tr.start()

        # current_fam_id = fam_queue.pop(0)

        # current_fam = add_family_id(current_fam_id, tree)

        # ids_to_process = []

        # ids_to_process.append(current_fam.get_husband())
        # ids_to_process.append(current_fam.get_wife())
        # for child_id in current_fam.get_children():
        #     ids_to_process.append(child_id)

        # person_threads = []
        # for person_id in ids_to_process:
        #     if person_id is not None:
        #         tr = Thread(target=add_person_id, args=(person_id, tree))
        #         person_threads.append(tr)
        #         tr.start()

        # for tr in person_threads:
        #     tr.join()

        # husband = tree.get_person(current_fam.get_husband())
        # wife = tree.get_person(current_fam.get_wife())
        # if husband.get_parentid() is not None:
        #     fam_queue.append(husband.get_parentid())
        # if wife.get_parentid() is not None:
        #     fam_queue.append(wife.get_parentid())

    if(len(fam_queue) == 0):
        print("Family queue is empty now")
        for tr in loop_threads:
            tr.join()

# -----------------------------------------------------------------------------
def breadth_fs_pedigree_limit5(family_id, tree):
    # semaphore to limit the connectionss
    # KEEP this function even if you don't implement it
    # TODO - implement breadth first retrieval
    #      - Limit number of concurrent connections to the FS server to 5
    # TODO - Printing out people and families that are retrieved from the server will help debugging

    pass
