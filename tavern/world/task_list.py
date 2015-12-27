from collections import defaultdict

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

    def add_task(self, nature, coord, task):
        self.employee_tasks[nature].append((coord, task))

    def remove_task(self, nature, coord, task):
        try:
            self.employee_tasks[nature].remove((coord, task))
            self.task_history.append((coord, task))
        except:
            print("Could not remove task %s (nature %s) at coords %s"
                  % (task, nature, coord))
            print("Current list : %s" % self.employee_tasks)
            print("History : %s" % self.task_history)
            raise Exception('Bad bad bad')
