import requests
from TaskRegistery import Registery
import time
import logging
from dataclasses import replace
import datetime

logging.basicConfig(level=logging.INFO)
MyRegistery = Registery()

class Scheduler:
    def __init__(self) -> None:
        self.registery = MyRegistery
        self.refresh_rate = 60
    
    def run(self):
        while True:
            for task_name, task_info in self.registery.known_tasks.items():
                logging.info(f"Checking task: {task_name} with status: {task_info.status} start time as {task_info.start_time} and next run at {datetime.datetime.fromtimestamp(task_info.next_run)}")
                if task_info.status == 'WAITING':
                    if self.check_time(task_info):
                        self.registery.known_tasks[task_name] = replace(task_info, status = 'RUNNING')
                        self.execute_task(task_info)
            time.sleep(self.refresh_rate)
            self.registery.refresh_tasks()

    def execute_task(self, task):
        try:
            output = task()
            return self.wrap_output(output, status='SUCCESS')
        except Exception as e:
            logging.error(f"Error occurred while executing task: {e}")
            return self.wrap_output(None, status='FAILED', error=str(e))
    
    def check_time(self, task):
        current_time = time.time()
        if task.next_run <= current_time:
            return True
        return False

    def wrap_output(self, output, status='FAILED', error=None):
        return {"status": status, "error": error, "output": output}

if __name__ == "__main__":
    scheduler = Scheduler()
    scheduler.run()