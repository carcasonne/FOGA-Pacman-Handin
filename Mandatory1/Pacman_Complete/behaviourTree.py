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
    def __init__(self, pac) -> None:
        self.pac = pac
        self.distanceToGhost = pac.ghosts

    def run(self):
        _, d = self.pac.closestGhostAndDistance()
        if d < 110:
            print("Ghost close TRUE")
            return True
        else:
            False


class BerserkMode(Task):
    def __init__(self, pac) -> None:
        self.pac = pac

    def run(self):
        ghost, d = self.pac.closestGhostAndDistance()
        if ghost.mode.current == FREIGHT and d < 200:
            print("Berserk Mode TRUE")
            return True
        return False


class Kill(Task):
    def __init__(self, pac) -> None:
        self.pac = pac

    def run(self):
        print("Kill mode: TRUE")
        self.pac.directionMethod = self.pac.getGhostDirection
        return True


class Flee(Task):
    def __init__(self, pac) -> None:
        self.pac = pac

    def run(self):
        print("Flee mode: TRUE")
        self.pac.directionMethod = self.pac.getDirectionAwayFromGhosts
        return True


class Wander(Task):
    def __init__(self, pac):
        self.pac = pac

    def run(self):
        self.pac.directionMethod = self.wanderBiased
        print(f"Trying to wander: {True}")
        return True

    def randomDirection(self, directions):
        return directions[randint(0, len(directions) - 1)]

    def wanderRandom(self, directions):
        return self.randomDirection(directions)

    def wanderBiased(self, directions):
        previousDirection = self.pac.direction
        if previousDirection in directions:
            nextDirProb = randint(1, 100)
            if nextDirProb <= 50:
                return previousDirection
            else:
                directions.remove(previousDirection)
                if directions == []:
                    return previousDirection
                else:
                    return choice(directions)
        else:
            return self.wanderRandom(directions)


class PowerPelletClose(Task):
    def __init__(self, pac) -> None:
        self.pac = pac

    def run(self):
        p, distance = self.pac.closestPelletWithDistance(True)
        close = distance < 120
        print(f"Power pellet close: {close}")
        print(distance)
        return close


class GetPowerPellets(Task):
    def __init__(self, pac) -> None:
        self.pac = pac

    def run(self):
        print("Get power pellet mode: TRUE")
        self.pac.directionMethod = self.pac.getPowerPelletDirection
        return True

class WanderForPellets(Task):
    def __init__(self, pac) -> None:
        self.pac = pac

    def run(self):
        print("Wander For Pellets: TRUE")
        self.pac.directionMethod = self.pac.getPelletDirection
        return True

class GoTopLeft(Task):
    def __init__(self, character):
        self.character = character

    def run(self):
        topLeft = Vector2(16, 64)
        self.character.setFlag()  # <-- FIXED FROM CODE PROVIDED
        self.character.directionMethod = self.character.goalDirection
        self.character.goal = topLeft
        return True


class Freeze(Task):
    def __init__(self, character):
        self.character = character

    def run(self):
        topLeft = Vector2(16, 64)
        if (self.character.position - topLeft).magnitude() < 2:
            self.character.freezeChar()
        return True


class IsFlagNotSet(Task):
    def __init__(self, character):
        self.character = character

    def run(self):
        if self.character.flag:
            return False
        else:
            return True
