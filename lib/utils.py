from math import sin, cos, radians
import numpy as np
from random import randint
from lib.config import cfg


def clamp(num, min_value, max_value):
   return max(min(num, max_value), min_value)

def flipy(y):
    return -y + cfg.world[1]

def random_world_position(border: int=0) -> tuple:
    x = randint(0+border, cfg.world[0]-border)
    y = randint(0+border, cfg.world[1]-border)
    return (x, y)