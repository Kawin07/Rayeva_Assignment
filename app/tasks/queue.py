from dataclasses import dataclass
from typing import Any, Callable
import logging


@dataclass
class TaskResult:
    success: bool
    data: Any = None
    error: str = ''


class TaskQueue:
    def submit(self, task_name: str, func: Callable, *args, **kwargs) -> TaskResult:
        try:
            result = func(*args, **kwargs)
            return TaskResult(success=True, data=result)
        except Exception as error:
            logging.getLogger('task_queue').exception('task_failed name=%s', task_name)
            return TaskResult(success=False, error=f'task_failed:{task_name}:{type(error).__name__}')


queue = TaskQueue()
