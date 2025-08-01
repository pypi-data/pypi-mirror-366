import logging
from concurrent.futures import ThreadPoolExecutor
from time import time, sleep

from taskshooter.config import DEBUG
from .task import Task

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, tasks: list[Task] = None, max_workers: int = None):
        self.tasks = tasks or []
        self.max_workers: int = max_workers or 5

    def run(self):
        self.show()

        while True:
            self.nap()
            self.workwork()

    def add(self, task: Task):
        self.tasks.append(task)

    def show(self):
        self.info("Scheduled tasks:")

        for task in self.tasks:
            self.info(f" * {task}: {task.trigger.description}")

    def workwork(self):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for task in self.tasks:
                if task.trigger.check():
                    executor.submit(task.run)

    def nap(self):
        seconds = 60 - time() % 60 + 0.1
        self.debug("💤 sleeping")
        sleep(seconds)

    # logging
    def log(self, level: int, message: str, exception: Exception = None):
        logger.log(level, message, exc_info=exception)

        if DEBUG:
            print(message)

    def debug(self, message: str, exception: Exception = None):
        self.log(logging.DEBUG, message, exception)

    def info(self, message: str, exception: Exception = None):
        self.log(logging.INFO, message, exception)

    def warning(self, message: str, exception: Exception = None):
        self.log(logging.WARNING, message, exception)

    def error(self, message: str, exception: Exception = None):
        self.log(logging.ERROR, message, exception)

    def exception(self, exception: Exception):
        self.error(str(exception), exception)
