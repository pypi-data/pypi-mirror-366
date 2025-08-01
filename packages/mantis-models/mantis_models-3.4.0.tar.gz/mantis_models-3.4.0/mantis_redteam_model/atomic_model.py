# -*- coding: utf-8 -*-
# mypy: ignore-errors
# flake8: noqa
from collections import OrderedDict
from enum import Enum
from typing import Dict
from typing import List

class Platform(str, Enum):
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"

    def __str__(self):
        return self.value


class ExecutorType(str, Enum):
    POWERSHELL = "powershell"
    BASH = "bash"
    COMMAND_PROMPT = "command_prompt"


class InputArguments:
    name: str
    description: str
    type: str
    default: str

    def __init__(self, name: str, description: str, type: str, default: str):
        self.name = name
        self.description = description
        self.type = type
        self.default = default


class Dependencies:
    description: str
    prereq_command: str
    get_prereq_command: str

    def __init__(self, description: str, prereq_command: str, get_prereq_command: str):
        self.description = description
        self.prereq_command = prereq_command
        self.get_prereq_command = get_prereq_command


class Executor:
    command: str
    name: str
    elevation_required: bool

    def __init__(self, command: str, name: str, elevation_required: bool):
        self.command = command
        self.name = name
        self.elevation_required = elevation_required


class Test:
    name: str
    auto_generated_guid: str
    description: str
    supported_platforms: List[Platform]
    input_arguments: List[InputArguments]
    dependency_executor_name: ExecutorType
    dependencies: List[Dependencies]
    executor: Executor
    worker_id: str

    def __init__(self, name: str):
        self.name = name
        self.supported_platforms = []
        self.input_arguments = []
        self.dependency_executor_name = []
        self.dependencies = []
        self.executor = None

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "supported_platforms": self.supported_platforms,
            "input_arguments": self.input_arguments,
            "dependency_executor_name": self.dependency_executor_name,
        }
