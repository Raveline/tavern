from collections import defaultdict
from itertools import chain


class TaskList(object):
    """
    The notion of a list of chores and various activities.
    """
    def __init__(self):
        # Tasks requiring an employee
        # Those are accessible with Functions as key
        # The values is a ((x, y), task) tuple
        self.employee_tasks = defaultdict(list)
        self.task_history = []
        self.ongoing_tasks = []

    def add_task(self, nature, coord, task):
        self.employee_tasks[nature].append((coord, task))

    def has_task(self, function):
        return bool(self.employee_tasks[function])

    def start_task(self, function, employee):
        started_task = self.employee_tasks[function].pop()
        self.ongoing_tasks.append((started_task, employee.name))
        return started_task

    def remove_task(self, nature, coord, task, success=False, employee=None):
        try:
            if employee is None:
                self.employee_tasks[nature].remove((coord, task))
                self.task_history.append((task, 'Cancelled'))
            else:
                display = 'Done'
                if not success:
                    display = 'Failed'
                self.ongoing_tasks.remove(((coord, task), employee.name))
                self.task_history.append((task, display))
        except ValueError:
            print("Could not remove task %s (id %s) (nature %s) at coords %s"
                  % (task, hex(id(task)), nature, coord))
            print("Current todo list : %s" % self.employee_tasks)
            print("Ongoing list : %s" % self.ongoing_tasks)
            print("All task list : %s" % self.all_tasks())
            raise Exception('Bad bad bad')

    def current_task_list(self):
        return [{'name': str(t[1]), 'status': 'To Do', 'owner': 'Nobody'} for t
                in chain.from_iterable(self.employee_tasks.values())]

    def previous_task_list(self):
        return [{'name': str(t[0]), 'status': 'Done', 'owner': 'Nobody'} for t
                in self.task_history]

    def ongoing_task_list(self):
        return [{'name': str(t[1]), 'status': 'Ongoing', 'owner': e}
                for t, e in self.ongoing_tasks]

    def all_tasks(self):
        return (self.current_task_list() +
                self.ongoing_task_list() +
                self.previous_task_list())
