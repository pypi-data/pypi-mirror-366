# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from enum import Enum
from logging import Logger
from typing import Dict, Optional, Type

try:
    from typing import Self

except ImportError:
    # For earlier versions...
    from typing_extensions import Self

from core_mixins.interfaces.factory import IFactory


class TaskStatus(str, Enum):
    CREATED = "CREATED"
    EXECUTING = "EXECUTING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class ITask(IFactory, ABC):
    """ Base implementations for different tasks/processes """

    def __init__(
            self, name: Optional[str] = None, description: Optional[str] = None,
            logger: Optional[Logger] = None) -> None:

        self._name = name
        self.description = description
        self._status = TaskStatus.CREATED
        self.logger = logger

    @classmethod
    def registration_key(cls) -> str:
        return cls.__name__

    @property
    def name(self):
        return self._name or self.__class__.__name__

    @property
    def status(self) -> TaskStatus:
        return self._status

    @status.setter
    def status(self, status: TaskStatus) -> None:
        self._status = status

    @abstractmethod
    def execute(self, *args, **kwargs):
        """ You must implement the task's process """

        self.info(f"Executing: {self.name}")
        self.info(f"Purpose: {self.description}")

    def info(self, message) -> None:
        if self.logger:
            self.logger.info(f"{self.name} | {message}")

    def warning(self, message) -> None:
        if self.logger:
            self.logger.warning(f"{self.name} | {message}")

    def error(self, error) -> None:
        if self.logger:
            self.logger.error(f"{self.name} | {error}")


class TaskException(Exception):
    """ Custom exception for Tasks """
