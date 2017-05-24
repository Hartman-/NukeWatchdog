import os
import re
import subprocess
import threading
import time


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


def watchdog(watch_path):
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

    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    threading.Thread(target=lambda: progress(proc), name='printer').start()


if __name__ == "__main__":
    print 'hello world'
    input_path = "/Users/ianhartman/Desktop/watchfolder"
    # watchdog(input_path)
    renderRegex()

