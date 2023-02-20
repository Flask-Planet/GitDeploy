from time import sleep

try:
    from environment import Environment
    from the_nightman import Supervisord, Gunicorn, supervisor_sock
except ImportError:
    from .environment import Environment
    from .the_nightman import Supervisord, Gunicorn, supervisor_sock


class Launcher:
    def __init__(self):
        self.env = Environment()
        self.supervisord = Supervisord()
        self.gunicorn = Gunicorn()

    def __enter__(self):
        self.supervisord.start()
        while True:
            sleep(1)
            if supervisor_sock.exists():
                break
        self.gunicorn.start()
        return "Running on: 0.0.0.0:9898 (Press Ctrl+C to stop)"

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


if __name__ == '__main__':
    with Launcher() as output:
        print(output)
