# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import json
import multiprocessing
import os
import psutil
import re
import subprocess
import threading
import time

from twisted.internet import defer, reactor, protocol
from twisted.internet.protocol import Factory


# Maintains a list of the jobs active in the queue
# Allows for easy updating of active/idling jobs
class ActivePool(object):
    def __init__(self):
        super(ActivePool, self).__init__()
        self.mgr = multiprocessing.Manager()
        self.active = self.mgr.list()
        self.lock = multiprocessing.Lock()

        self.status = {}

    def makeActive(self, name):
        with self.lock:
            self.active.append(name)

    def makeInactive(self, name):
        with self.lock:
            self.active.remove(name)

    def setProgress(self, name, prog):
        with self.lock:
            cur_frame = prog[0]
            cur_progress = prog[1]
            cur_total = prog[2]

            percentage = (float(cur_progress) / float(cur_total)) * 100

            self.status[name] = {
                'percent': percentage,
                'curf': cur_frame,
                'chunkf': cur_progress,
                'totalf': cur_total
            }

            # print '%s %s%s' % (multiprocessing.current_process().name, int(percentage), '%')

    # Once the job clears, pop the key from the dictionary store
    def removeStatus(self, name):
        with self.lock:
            self.status.pop(name, None)

    def currentProgress(self, name):
        with self.lock:
            if name in self.status:
                return self.status[name]['percent']

    def currentActive(self):
        with self.lock:
            return str(self.active)

    def __str__(self):
        with self.lock:
            return str(self.active)


# Thread target to check the queue on a constant interval
# Adds idle sleep process if the queue is empty
def checkQueue(in_queue, num, pool):
    # Let the pool grab any tasks if any exist
    print 'fuck you %s' % threading.current_thread()

    while True:
        # print 'Running: %s' % str(pool)
        if in_queue.empty():
            idle_tasks = []

            # always add # of processes + one to make sure that the queue is full for a moment
            # Resets check
            for i in range(num + 1):
                # give the process a task to basically idle

                winIdleTask = {
                    'name': 'IDLE_JOB_%s' % i,
                    'env': {
                        'user': 'system'
                    },
                    'cmd': ['TIMEOUT', '10']
                }

                unixIdleTask = {
                    'name': 'IDLE_JOB_%s' % i,
                    'env': {
                        'user': 'system'
                    },
                    'cmd': ['sleep', '10']
                }

                # Windows has a different sleep command
                if psutil.WINDOWS:
                    idle_tasks.append(winIdleTask)
                else:
                    idle_tasks.append(unixIdleTask)

            for task in idle_tasks:
                in_queue.put(task)

        sleep(2)
        print 'hello'


def dump_queue(queue):
    """
    Empties all pending items in a queue and returns them in a list.
    """
    result = []
    print queue.get
    # for i in iter(queue.get, 'STOP'):
    #     result.append(i)
    # sleep(.1)
    # return result


# Nuke and subprocess communicate aren't buddies, quick printer to check the progress
def progress(proc, pool):
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
            frame_data = re.findall(r"\d+", line)
            cur_process = multiprocessing.current_process()

            if len(frame_data) > 1:
                pool.setProgress(cur_process.name, frame_data)

            # print '[PROGRESS] %s' % line
            print pool.currentProgress(cur_process.name)


def sleep(secs):
    d = defer.Deferred()
    reactor.callLater(secs, d.callback, None)
    return d


# Simple multiprocessing process work submit function
def worker_main(queue, pool):
    print 'PID [%s] - Started' % os.getpid()

    while True:
        item = queue.get(True)

        # Set the name of the process
        name = item['name']
        cmd = item['cmd']
        multiprocessing.current_process().name = name

        pool.makeActive(name)

        custom_env = os.environ.copy()

        for key in item['env']:
            custom_env[key.upper()] = item['env'][key]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=custom_env)
        progress(process, pool)

        pool.makeInactive(name)
        pool.removeStatus(name)
        # print 'PID [%s] - GET - %s' % (os.getpid(), item)


class ManagerProtocol(protocol.Protocol):
    """This is just about the simplest possible protocol"""

    def dataReceived(self, data):
        print data
        "As soon as any data is received, write it back."
        task = {
            'name': 'NUKE_JOB_0',
            'env': {
                'seq': 'abc',
                'shot': '010',
                'user': 'imh29'
            },
            'cmd': [
                "/Applications/Nuke10.5v4/Nuke10.5v4.app/Contents/MacOS/Nuke10.5v4",
                "--nukex",
                "-i",
                "-F",
                "1-10",
                "-X",
                "Write1",
                "/Users/ianhartman/Desktop/footage_tracking/_source/track_v001.nk"]
        }

        json_test = json.dumps(task)
        self.factory.active_queue.makeActive(task['name'])
        print str(self.factory.active_queue)
        self.transport.write(json_test)


# PUT ALL THE PERSISTENT DEFINITIONS HERE!!!!
# starting to make a bit of sense now...
class ManagerFactory(Factory):
    num_connections = 0
    active_queue = ActivePool()

    protocol = ManagerProtocol

    def __init__(self, num_processes):
        print 'Starting up... '

        # I guess I would build my queue and pool here... neat
        self.processes = int(num_processes)

        self.queue = multiprocessing.Queue()
        self.pool = multiprocessing.Pool(self.processes, worker_main, (self.queue,
                                                                       self.active_queue,))

        self.startWatcher(self.queue, self.processes, self.pool)

        # Close the pool
        self.pool.close()
        self.pool.join()

    def startWatcher(self, queue, processes, pool):
        queue_watcher = threading.Thread(target=checkQueue, name='QueueWatcher', args=(queue,
                                                                                       processes,
                                                                                       pool))
        queue_watcher.setDaemon(True)
        queue_watcher.start()

    def currentQueue(self):
        queue_list = dump_queue(self.queue)
        print queue_list

    def addTask(self, input_task):
        self.queue.put(input_task)


def main():
    """This runs the protocol on port 8000"""
    reactor.listenTCP(8000, ManagerFactory(2))
    reactor.run()


# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()