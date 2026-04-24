from enum import Enum
import time
import psutil

class status(Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    ERROR = 'error'

class task:
    def __init__(self, name, description, function):
        self.name = name
        self.description = description
        self.function = function
        self.cpu_usage = 0
        self.memory_usage = 0
        self.status = status.PENDING
        self.duration = 0
    
    def run(self):
        import threading
        import time
        self.status = status.RUNNING
        self.thread = threading.Thread(target=self.__wrapper)
        self.start_time = time.time()
        self.thread.start()
    
    def update_status(self):
        if self.thread.is_alive():
            self.cpu_usage = psutil.cpu_percent(interval=1)
            self.memory_usage = psutil.virtual_memory().percent
            self.duration = time.time() - self.start_time
            time.sleep(1)

    def __wrapper(self):
        try:
            self.function()
            self.status = status.COMPLETED
            self.duration = time.time() - self.start_time
        except Exception as e:
            self.status = status.ERROR
            self.error = str(e)
            self.duration = time.time() - self.start_time

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['thread']
        del state['function']
        return state

    def get_status(self):
        return self.__getstate__()