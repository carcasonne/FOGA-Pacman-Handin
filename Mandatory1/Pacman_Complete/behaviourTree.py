from pydoc import classname
from vector import Vector2
from constants import *
import numpy
from random import randint, choice
import math
from algorithms import *


class Task(object):
    # Always terminates with either success (True) or failure (False)
    def run(self) -> bool:
        raise NotImplementedError()

    def __str__(self) -> str:
        return self.__class__.__name__


class Selector(Task):
    def __init__(self, children):
        self.children = children

    def run(self):
        for c in self.children:
            if c.run():
                # print(str(c) + ":" + str(True))
                return True
            # print(str(c) + ":" + str(False))
        return False


class Sequence(Task):
    def __init__(self, children):
        self.children = children

    def run(self):
        for c in self.children:
            if not c.run():
                # print(str(c) + ":" + str(False))
                return False
            # print(str(c) + ":" + str(True))
        return True


enemyCloseDistance = 15


class GhostClose(Task):
    def __init__(self, pac, distanceThreshold) -> None:
        self.pac = pac
        self.distanceThreshold = distanceThreshold

    def run(self):
        _, d = self.pac.closestGhostAndDistance()
        if d < self.distanceThreshold:
            # print("Ghost close TRUE")
            return True
        else:
            return False


class BerserkMode(Task):
    def __init__(self, pac, distanceThreshold) -> None:
        self.pac = pac
        self.distanceThreshold = distanceThreshold

    def run(self):
        for ghost in self.pac.ghosts:
            dist = (self.pac.position - ghost.position).magnitude()
            if ghost.mode.current == FREIGHT and dist < self.distanceThreshold:
                return True
        return False


class Kill(Task):
    def __init__(self, pac) -> None:
        self.pac = pac

    def run(self):
        self.pac.directionMethod = self.pac.getGhostDirection
        return True


class Flee(Task):
    def __init__(self, pac) -> None:
        self.pac = pac

    def run(self):
        # print("Flee mode: TRUE")
        self.pac.directionMethod = self.pac.getDirectionAwayFromGhosts
        return True


class GhostWillCollide(Task):
    def __init__(self, pac) -> None:
        self.pac = pac

    def run(self):
        for ghost in self.pac.ghosts:
            if ghost.target == self.pac.target and ghost.node != self.pac.node:
                return True
        return False


class Reverse(Task):
    def __init__(self, pac) -> None:
        self.pac = pac

    def run(self):
        print("changing to getReverseDirection")
        self.pac.directionMethod = self.pac.getReverseDirection
        return True


class PowerPelletClose(Task):
    def __init__(self, pac, distanceThreshold) -> None:
        self.pac = pac
        self.distanceThreshold = distanceThreshold

    def run(self):
        p, distance = self.pac.closestPelletWithDistance(True)
        close = distance < self.distanceThreshold
        return close


class GetPowerPellets(Task):
    def __init__(self, pac) -> None:
        self.pac = pac

    def run(self):
        # print("Get power pellet mode: TRUE")
        self.pac.directionMethod = self.pac.getPowerPelletDirection
        return True


class WanderForPellets(Task):
    def __init__(self, pac) -> None:
        self.pac = pac

    def run(self):
        # print("Wander For Pellets: TRUE")
        self.pac.directionMethod = self.pac.getPelletDirection
        return True
