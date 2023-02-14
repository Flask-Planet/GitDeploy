"""fighter of the dayman"""

import threading
import time
from pathlib import Path

from .terminator import Terminator


def text_log(text):
    with open("logs/the_night_man.log", "a") as f:
        f.write(f"{time.ctime()} => {text}\n")


class BackgroundTasks(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self, *args, **kwargs):
        with Terminator("venv/bin/supervisord", working_directory=Path.cwd()) as run:
            out, err = run("-c supervisor/supervisord.conf -n")
            text_log(f"{Path.cwd()}")
            text_log(f"{out} {err}")
