from enum import Enum


class DialogStatus(Enum):
    success = 0
    failure = 1
    terminated = 2
    incomplete = 3