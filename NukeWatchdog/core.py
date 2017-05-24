import multiprocessing
import os
import Queue
import random
import re
import subprocess
import threading
import time

# Instantiate the job queue
# job_queue = Queue.Queue()


class ActivePool(object):
    def __init__(self):
        super(ActivePool, self).__init__()
        self.manager = multiprocessing.Manager()
        self.active = self.manager.list()
        self.lock = multiprocessing.Lock()

    def makeActive(self, name):
        with self.lock:
            self.active.append(name)

    def makeInactive(self, name):
        with self.lock:
            self.active.remove(name)

    def __str__(self):
        with self.lock:
            return str(self.active)


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
            cur_thread = threading.current_thread()
            print cur_thread.name
            print '[PROGRESS] %s' % line


def watch_directory(watch_path):
    before = dict([(f, None) for f in os.listdir(watch_path)])
    while 1:
        time.sleep(10)

        after = dict([(f, None) for f in os.listdir(watch_path)])
        added = [f for f in after if f not in before]
        removed = [f for f in before if f not in after]

        if added:
            print "Added: ", ", ".join(added)
        if removed:
            print "Removed: ", ", ".join(removed)
        before = after


def render_worker(s, args):
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    threading.Thread(target=lambda: progress(proc), name='printer').start()
    return proc


def renderRegex():
    args = [
        "/Applications/Nuke10.5v4/Nuke10.5v4.app/Contents/MacOS/Nuke10.5v4",
        "--nukex",
        "-i",
        "-F",
        "1-10",
        "-X",
        "Write1",
        "/Users/ianhartman/Desktop/footage_tracking/_source/track_v001.nk"
    ]

    # proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    # threading.Thread(target=lambda: progress(proc), name='printer').start()
    job_queue.put(render_worker(args))


def worker(s, pool):
    name = multiprocessing.current_process().name
    with s:
        pool.makeActive(name)
        print 'Starting: %s' % str(pool)
        time.sleep(random.random())
        pool.makeInactive(name)

if __name__ == "__main__":
    # input_path = "/Users/ianhartman/Desktop/watchfolder"
    # watch_directory(input_path)
    # renderRegex()

    pool = ActivePool()
    s = multiprocessing.Semaphore(2)
    jobs = [
        multiprocessing.Process(target=worker, name=str(i), args=(s, pool))
        for i in range(10)
    ]

    for j in jobs:
        j.start()

    for j in jobs:
        j.join()
        print 'Now running: %s' % str(pool)


