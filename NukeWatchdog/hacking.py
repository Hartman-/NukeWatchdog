import multiprocessing
import os
import subprocess
import re
import time


def worker_main(queue):
    print 'PID [%s] - Started' % os.getpid()
    while True:
        item = queue.get(True)
        process = subprocess.Popen(item, stdout=subprocess.PIPE)
        progress(process)
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


if __name__ == '__main__':
    NUMBER_OF_PROCESSES = 2
    the_queue = multiprocessing.Queue()
    the_pool = multiprocessing.Pool(NUMBER_OF_PROCESSES, worker_main, (the_queue, ))

    # for i in range(NUMBER_OF_PROCESSES):
    #     multiprocessing.Process(target=worker_main, args=(the_queue,)).start()

    tasks = [[
        "/Applications/Nuke10.5v4/Nuke10.5v4.app/Contents/MacOS/Nuke10.5v4",
        "--nukex",
        "-i",
        "-F",
        "1-10",
        "-X",
        "Write1",
        "/Users/ianhartman/Desktop/footage_tracking/_source/track_v001.nk"
    ], [
        "/Applications/Nuke10.5v4/Nuke10.5v4.app/Contents/MacOS/Nuke10.5v4",
        "--nukex",
        "-i",
        "-F",
        "21-30",
        "-X",
        "Write1",
        "/Users/ianhartman/Desktop/footage_tracking/_source/track_v001.nk"
    ]]
    for task in tasks:
        the_queue.put(task)

    time.sleep(2)
    new_tasks = [[
        "/Applications/Nuke10.5v4/Nuke10.5v4.app/Contents/MacOS/Nuke10.5v4",
        "--nukex",
        "-i",
        "-F",
        "41-50",
        "-X",
        "Write1",
        "/Users/ianhartman/Desktop/footage_tracking/_source/track_v001.nk"
    ], [
        "/Applications/Nuke10.5v4/Nuke10.5v4.app/Contents/MacOS/Nuke10.5v4",
        "--nukex",
        "-i",
        "-F",
        "61-70",
        "-X",
        "Write1",
        "/Users/ianhartman/Desktop/footage_tracking/_source/track_v001.nk"
    ]]
    for newtask in new_tasks:
        the_queue.put(newtask)

    the_pool.close()
    the_pool.join()