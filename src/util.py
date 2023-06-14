from enum import Enum
import pygame

# Helper functions
def interp(n: int, from1: int, to1: int, from2: int, to2: int):
    """Interpolates a number from one range to another range"""
    return (n - from1) / (to1 - from1) * (to2 - from2) + from2


def equals(a: float, b: float, within: float):
    """Checks if two numbers are equal within a certain tolerance."""
    return abs(a - b) <= within


# Enums
class State(Enum):
    """Holds a cell's state, open or occupied"""
    OPEN = 0
    WATER = 1
    BLOCKED = 2

class Team(Enum):
    NEUTRAL = 0
    RED = 1
    GREEN = 2

