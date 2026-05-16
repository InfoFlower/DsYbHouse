from dataclasses import dataclass
from TaskEngine import TaskEngine


def check_date(string):
    if len(string) != 5:
        return False
    for i, ch in enumerate(string):
        if i == 2:
            if ch != ':':
                return False
        else:
            if not ch.isdigit():   # checks if ch is a digit character
                return False
    return True

def checker(Task):
    pass

@dataclass(frozen=True)
class TaskInfo:
    # Metadata
    name : str = 'Single_Task'
    desc : str = 'Just a task'
    file : str = 'single_task.py'
    path : str = './src_batch/tasks/' 
    
    # engine
    status : str|None = None 
    timeout : int = 0
    engine : TaskEngine|None = TaskEngine(path, timeout)

    # Regular run
    day_of_week : int = 0
    periodicity : str = 'day'
    start_time : str = '00:00'
    reload : bool = False 
    
    # Forced run
    Forced : bool = False
    Forced_start_time : str|None = None #'00:00'

    next_run : str = '00:00'

    def __post_init__(self):
        if not check_date(self.start_time):
            raise ValueError(f'start_time bad format "{self.start_time}"')
        if self.Forced:
            if not check_date(self.Forced_start_time) :
                raise ValueError(f'Forced_start_time bad format "{self.Forced_start_time}"')