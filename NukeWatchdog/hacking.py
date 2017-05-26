import multiprocessing
import os
import subprocess
import re
import time
import threading
import psutil


POOL_RUNNING = False


# Maintains a list of the jobs active in the queue
# Allows for easy updating of active/idling jobs
class ActivePool(object):
    def __init__(self):
        super(ActivePool, self).__init__()
        self.mgr = multiprocessing.Manager()
        self.active = self.mgr.list()
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


# Simple multiprocessing process work submit function
def worker_main(queue, pool):
    print 'PID [%s] - Started' % os.getpid()

    while True:
        item = queue.get(True)

        # Set the name of the process
        name = item.pop(0)
        multiprocessing.current_process().name = name

        pool.makeActive(name)

        custom_env = os.environ.copy()
        custom_env['TEST'] = '%sPROCESS' % os.getpid()
        process = subprocess.Popen(item, stdout=subprocess.PIPE, env=custom_env)
        progress(process)

        pool.makeInactive(name)
        # print 'PID [%s] - GET - %s' % (os.getpid(), item)


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
            cur_process = multiprocessing.current_process()
            print cur_process.name
            print '[PROGRESS] %s' % line


def poolRunning():
    return POOL_RUNNING


# Thread target to check the queue on a constant interval
# Adds idle sleep process if the queue is empty
def checkQueue(in_queue, num, pool):
    # Let the pool grab any tasks if any exist
    time.sleep(5)

    while True:
        print 'Running: %s' % str(pool)
        if in_queue.empty():
            idle_tasks = []

            # always add # of processes + one to make sure that the queue is full for a moment
            # Resets check
            for i in range(num + 1):
                # give the process a task to basically idle
                print i

                # Windows has a different sleep command
                if psutil.WINDOWS:
                    idle_tasks.append(["IDLE_JOB_%s" % i, 'TIMEOUT', '10'])
                else:
                    idle_tasks.append(["IDLE_JOB_%s" % i, 'sleep', '10'])

            for task in idle_tasks:
                in_queue.put(task)
        time.sleep(3)

        # Need a better way to set running status
        if not poolRunning():
            break


if __name__ == '__main__':
    active_pool = ActivePool()

    NUMBER_OF_PROCESSES = 2
    the_queue = multiprocessing.Queue()
    the_pool = multiprocessing.Pool(NUMBER_OF_PROCESSES, worker_main, (the_queue, active_pool, ))
    POOL_RUNNING = True

    # Setup thread to constantly check the queue for tasks
    queue_watcher = threading.Thread(target=checkQueue, name='QueueWatch', args=(the_queue,
                                                                                 NUMBER_OF_PROCESSES,
                                                                                 active_pool))
    queue_watcher.setDaemon(True)
    queue_watcher.start()

    tasks = [[
        "NUKE_JOB_0",
        "/Applications/Nuke10.5v4/Nuke10.5v4.app/Contents/MacOS/Nuke10.5v4",
        "--nukex",
        "-i",
        "-F",
        "1-10",
        "-X",
        "Write1",
        "/Users/ianhartman/Desktop/footage_tracking/_source/track_v001.nk"
    ], [
        "NUKE_JOB_1",
        "/Applications/Nuke10.5v4/Nuke10.5v4.app/Contents/MacOS/Nuke10.5v4",
        "--nukex",
        "-i",
        "-F",
        "21-30",
        "-X",
        "Write1",
        "/Users/ianhartman/Desktop/footage_tracking/_source/track_v001.nk"
    ],[
        "NUKE_JOB_2",
        "/Applications/Nuke10.5v4/Nuke10.5v4.app/Contents/MacOS/Nuke10.5v4",
        "--nukex",
        "-i",
        "-F",
        "41-50",
        "-X",
        "Write1",
        "/Users/ianhartman/Desktop/footage_tracking/_source/track_v001.nk"
    ]]
    for task in tasks:
        the_queue.put(task)

    # Effectively close the pool
    the_pool.close()
    the_pool.join()
