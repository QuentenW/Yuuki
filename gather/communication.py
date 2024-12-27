#### Data
from collections import namedtuple
from enum import Flag, auto


SaveData = namedtuple('SaveData', ['timestamp', 'position', 'imgFrame'])

# NOTE: Add more signal types here for controlling hardware process
class CommandSignal(Flag):
  EXIT = auto()