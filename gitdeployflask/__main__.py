from environment import Environment
from the_nightman import Supervisord, Gunicorn


class Launcher:
    def __init__(self):
        self.supervisord = Supervisord()
        self.gunicorn = Gunicorn()
        self.env = Environment()

    def __enter__(self):
        self.supervisord.start()
        self.gunicorn.start()
        return "Running... (Press Ctrl+C to stop)"

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


with Launcher() as output:
    print(output)
