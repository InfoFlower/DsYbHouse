from src_batch.AUTOMATE.TASKS import task

class scheduler:
    def __init__(self, **args):
        self.schedule = []
        self.running_tasks = []
        self.max_concurrent_tasks = args.get('max_concurrent_tasks', 1)
        self.timeout = args.get('timeout', 1)
        self.refresh_rate = args.get('refresh_rate', 1)
    
    def add_scheduled_task(self, task, start_time, dependency=None):
        for i, scheduled_task in enumerate(self.schedule):
            if scheduled_task['start_time'] > start_time:
                self.schedule.insert(i, {'task': task, 
                                         'start_time': start_time, 
                                         'dependency': dependency})
    
    
    def run(self):
