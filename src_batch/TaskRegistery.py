import json
import datetime
from TaskUnit import TaskInfo
from dataclasses import asdict, replace
import os
from dotenv import load_dotenv
load_dotenv()
WD = os.getenv('WD')
WD_PATH = WD + '/src_batch' #type:ignore


class Registery:
    def __init__(self, folder : str = './tasks') -> None:
        self.task_folder = folder
        self.known_tasks : dict = self.refresh_tasks()

    def link_tasks(self) -> dict:
        with open(WD_PATH+'/Task_infos.json','r') as f:
            tasks_metadata = json.load(f)
        params_tasks = tasks_metadata['tasks']
        all_tasks = {}
        for task_name, params in params_tasks.items() :
            Current_task = TaskInfo(name=task_name,
                                    desc=params['desc'],
                                    file=params['file'],
                                    status='WAITING',
                                    day_of_week=params['day_of_week'],
                                    start_time=params['start_time'],
                                    periodicity=params['periodicity'],
                                    timeout=params['timeout'],
                                    reload=params['reload'],
                                    path=self.task_folder+f"/{params['file']}")
            Current_task = replace(Current_task, next_run = self.calculate_next_run(Current_task))
            all_tasks[task_name] = (Current_task)
        return all_tasks
    
    def show_tasks(self):
        return [i for i in self.known_tasks]#type:ignore

    def refresh_tasks(self) -> dict:
        try :
            return self.link_tasks()
        except ValueError as e :
            print(e)
            return {}
    
    def __getitem__(self, key):
        return self.known_tasks[key]
    
    def calculate_next_run(self, task : TaskInfo):
        if task.periodicity == 'day':
            return calcule_daily(task.start_time)
        if task.periodicity == 'week':
            return calcule_weekly(task.day_of_week, task.start_time)

    def make_frame(self):
        frame = f"   Task_name{' ' * 21}Description{' ' * 21}Status\n"
        frame += f"{'-'*75}\n"
        for task_name, task_info in self.known_tasks.items():
            frame += f"{task_name}{' ' * 10 +'|' + ' ' * 10}{task_info.desc}{' ' * 10 +'|' + ' ' * 10}{task_info.status}\n\n"
        frame += f"{'-'*75}\n"
        return frame

def calcule_daily(start_time, setup_daily=True):
    current_day = datetime.datetime.now().date()
    hour, minute = map(int, start_time.split(":"))
    time = datetime.time(hour, minute)
    target_timestamp = datetime.datetime.combine(current_day, time).timestamp()
    hour, minute = map(int, start_time.split(":"))
    if setup_daily and target_timestamp < datetime.datetime.now().timestamp():
        target_timestamp += 24 * 3600
    return target_timestamp


def calcule_weekly(day_of_week, start_time):
    current_timestamp = datetime.datetime.now().timestamp()
    wanted_timestamp = calcule_daily(start_time, setup_daily=False)
    current_weekday = datetime.datetime.now().date().weekday()
    if current_weekday < day_of_week or (current_weekday == day_of_week and wanted_timestamp > current_timestamp):
        days_until_next_run = (day_of_week - current_weekday) % 7
    else:
        days_until_next_run = day_of_week - current_weekday 
    return wanted_timestamp + days_until_next_run * 24 * 3600