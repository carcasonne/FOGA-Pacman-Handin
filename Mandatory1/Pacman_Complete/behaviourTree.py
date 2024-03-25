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
                #print(str(c) + ":" + str(True))
                return True
            #print(str(c) + ":" + str(False))
        return False


class Sequence(Task):
    def __init__(self, children):
        self.children = children

    def run(self):
        for c in self.children:
            if not c.run():
                #print(str(c) + ":" + str(False))
                return False
            #print(str(c) + ":" + str(True))
        return True


enemyCloseDistance = 15

class GhostClose(Task):
    def __init__(self, pac) -> None:
        self.pac = pac
        self.distanceToGhost = pac.ghosts
    
    def run(self):
        _, d = self.pac.closestGhostAndDistance()
        if d < 100:
            print("Ghost close TRUE")
            return True
        else:
            False

class BerserkMode(Task):
    def __init__(self, pac) -> None:
        self.pac = pac
    
    def run(self):
        for ghost in self.pac.ghosts:
            if ghost.mode.current == FREIGHT:
                print("Berserk Mode TRUE")
                return True
        return False

class Kill(Task):
    def __init__(self, pac) -> None:
        self.pac = pac
    
    def run(self):
        self.pac.directionMethod = self.kill
        return True
    
    def kill(self, directions):
        print(f"Trying to kill")
        distances = []
        g, _ = self.pac.closestGhostAndDistance()
        for direction in directions:
            vec = (
                g.position
                - self.pac.node.position
                + self.pac.directions[direction] * TILEWIDTH
            )
            distances.append(vec.magnitudeSquared())
            
        index = distances.index(max(distances))
        return directions[index]


class Flee(Task):
    def __init__(self, pac) -> None:
        self.pac = pac

    def run(self):
        self.pac.directionMethod = self.flee
        return True

    def flee(self, directions):
        print("Trying to flee")
        distances = []
        g, _ = self.pac.closestGhostAndDistance()
        for direction in directions:
            vec = (
                g.position
                - self.pac.node.position
                + self.pac.directions[direction] * TILEWIDTH
            )
            distances.append(vec.magnitudeSquared())
            
        index = distances.index(min(distances))
        return directions[index]

class EnemyFar(Task):
    def __init__(self, distanceToEnemy: float):
        self.distanceToEnemy = distanceToEnemy

    def run(self):
        if self.distanceToEnemy > enemyCloseDistance:
            return True
        else:
            return False

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


class GetPowerPellets(Task):
    def __init__(self, pac) -> None:
        self.pac = pac
        self.pp = self.pac.pp

    def run(self):
        closestPellet, _ = self.pac.closestPelletWithNode()
        if(closestPellet == None):
            return False
        self.pac.directionMethod = self.seek
        print("Trying to get power pellet")
        return True

    def seek(self, directions):
        # Dijkstra from pacman to pellets
        pacmanTarget = self.pac.target        
        previous_nodes = non_fucked_dijkstra(self.pac.nodes, pacmanTarget)
        closestPellet, _ = self.pac.closestPelletWithNode()

        pp_node = self.pac.nodes.getNodeFromPixels(closestPellet.position.x, closestPellet.position.y)
        path = []
        prev = pp_node
        while(prev != None):
            path.append(prev)
            prev = previous_nodes[prev]
        list.reverse(path)
        
        if len(path) == 0:
            return directions[0]

        direction = directions[0]

        for nDir in directions:
            node = pacmanTarget.neighbors[nDir]
            if node in path:
                direction = nDir
        return direction

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
