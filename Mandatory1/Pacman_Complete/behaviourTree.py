from pydoc import classname
from vector import Vector2


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
                print(str(c) + ":" + str(True))
                return True
            print(str(c) + ":" + str(False))
        return False


class Sequence(Task):
    def __init__(self, children):
        self.children = children

    def run(self):
        for c in self.children:
            if not c.run():
                print(str(c) + ":" + str(False))
                return False
            print(str(c) + ":" + str(True))
        return True


enemyCloseDistance = 15


class EnemyFar(Task):
    def __init__(self, distanceToEnemy: float):
        self.distanceToEnemy = distanceToEnemy

    def run(self):
        if self.distanceToEnemy > enemyCloseDistance:
            return True
        else:
            return False


class Wander(Task):
    def __init__(self, character):
        self.character = character

    def run(self):
        self.character.directionMethod = self.character.wanderBiased
        return True


class EnemyNear(Task):
    def __init__(self, distanceToEnemy):
        self.distanceToEnemy = distanceToEnemy

    def run(self):
        if self.distanceToEnemy <= enemyCloseDistance:
            return True
        else:
            return False


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
