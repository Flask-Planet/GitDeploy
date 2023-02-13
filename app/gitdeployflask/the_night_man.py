"""enemy of the day man"""

import threading
import time

from .terminator import Terminator


def text_log(text):
    with open("logs/the_night_man.log", "a") as f:
        f.write(f"{time.ctime()} => {text}\n")


class BackgroundTasks(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self, *args, **kwargs):
        with Terminator() as run:
            out, err = run("supervisord -c supervisor/supervisord.conf -n")
            if err:
                text_log(f"{err}")
                raise SystemExit("Supervisor failed to start")
