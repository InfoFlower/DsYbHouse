import subprocess

class TaskEngine:
    def __init__(self, path, timeout = 60):
        self.path = path
        self.timeout = timeout
    
    def __call__(self):
        try :
            run = subprocess.run(
                ['python', self.path],
                timeout=self.timeout
            )
            return run
        except Exception as e:
            return {'STATUS' : 'TIMEOUT', 'TASK' : e.args[0], 'TIME' : e.args[1]}