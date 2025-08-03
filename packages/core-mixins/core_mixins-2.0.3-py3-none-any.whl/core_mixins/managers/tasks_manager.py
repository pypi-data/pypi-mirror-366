# -*- coding: utf-8 -*-

from multiprocessing.pool import Pool
from typing import Dict, List

from core_mixins.interfaces.task import ITask
from core_mixins.interfaces.task import TaskStatus


class TasksManager:
    """ It manages the execution for the registered tasks """

    def __init__(self, tasks: List[ITask]):
        self.tasks = tasks

    def execute(
            self, task_name: str = None, parallelize: bool = False,
            processes: int = None) -> List[Dict]:

        """
        Execute all registered tasks. An exception in one task should not
        stop the execution of the others...

        Example of results:

        .. code-block:: python

            [
                { "status": "Ok", "result": ... },
                { "status": "Failed", "error": ... }
            ]
        ..

        :param task_name: If defined, only that specific task will be executed.
        :type task_name: str
        :param parallelize: It defines if you want to execute the tasks in parallel.
        :type parallelize: bool
        :param processes: Number of parallel process.
        :type processes: int

        :return: The list of the execution results.
        :rtype: List[Dict]
        """

        if task_name:
            for task in self.tasks:
                if task_name == task.name:
                    return [execute(task)]

        res = []
        if not parallelize:
            for task in self.tasks:
                res.append(execute(task))

        else:
            with Pool(processes=processes) as pool:
                res = pool.map(execute, (task for task in self.tasks))

        return res


def execute(task: ITask):
    try:
        return {
            "status": TaskStatus.SUCCESS,
            "result": task.execute()
        }

    except Exception as error:
        return {
            "status": TaskStatus.ERROR,
            "error": error
        }
