#
# Simple example which uses a pool of workers to carry out some tasks.
#
# Notice that the results will probably not come out of the output
# queue in the same in the same order as the corresponding tasks were
# put on the input queue.  If it is important to get the results back
# in the original order then consider using `Pool.map()` or
# `Pool.imap()` (which will save on the amount of code needed anyway).
#
# Copyright (c) 2006-2008, R Oudkerk
# All rights reserved.
#

import time
import re
from multiprocessing import Process, Queue, current_process, freeze_support
import subprocess
import threading


#
# Function run by worker processes
#

def worker(input, output):
    for func, args in iter(input.get, 'STOP'):
        process = subprocess.Popen(input.get(), stdout=subprocess.PIPE)
        threading.Thread(target=lambda: progress(process), name='printer').start()
        # time.sleep(1)
        output.put('done')


# Nuke and subprocess communicate aren't buddies.
def progress(proc):
    """
    Prints the progress of the thread.

    :param proc: Input process to print the progress of.
    :return: None
    """
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        if re.match(r"Frame\s+", line):
            cur_process = threading.current_thread()
            print cur_process.name
            print '[PROGRESS] %s' % line


def run():
    NUMBER_OF_PROCESSES = 2
    TASKS1 = [[
        "/Applications/Nuke10.5v4/Nuke10.5v4.app/Contents/MacOS/Nuke10.5v4",
        "--nukex",
        "-i",
        "-F",
        "1-10",
        "-X",
        "Write1",
        "/Users/ianhartman/Desktop/footage_tracking/_source/track_v001.nk"
    ]]
    TASKS2 = [[
        "/Applications/Nuke10.5v4/Nuke10.5v4.app/Contents/MacOS/Nuke10.5v4",
        "--nukex",
        "-i",
        "-F",
        "21-30",
        "-X",
        "Write1",
        "/Users/ianhartman/Desktop/footage_tracking/_source/track_v001.nk"
    ]]

    # Create queues
    task_queue = Queue()
    done_queue = Queue()

    # Submit tasks
    for task in TASKS1:
        task_queue.put(task)

    # Start worker processes
    for i in range(NUMBER_OF_PROCESSES):
        Process(target=worker, args=(task_queue, done_queue)).start()

    # Add more tasks using `put()`
    for task in TASKS2:
        task_queue.put(task)

    # # Get and print some more results
    # for i in range(task_queue.qsize()):
    #     print '\t', done_queue.get()
    #
    # # Tell child processes to stop
    # for i in range(NUMBER_OF_PROCESSES):
    #     task_queue.put('STOP')


if __name__ == '__main__':
    freeze_support()
    run()
