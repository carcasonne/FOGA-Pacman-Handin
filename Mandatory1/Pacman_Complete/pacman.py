import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
from behaviourTree import *
import random


class Pacman(Entity):
    def __init__(self, node, powerpellets, pellets, nodes):
        Entity.__init__(self, node)
        self.name = PACMAN
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.pp = powerpellets
        self.pellets = pellets
        # Ghosts and pacman have recursive constructors
        self.ghosts = None
        self.nodes = nodes

    def updateGhosts(self, ghosts):
        self.ghosts = ghosts

    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.image = self.sprites.getStartImage()
        self.sprites.reset()

    def die(self):
        self.alive = False
        self.direction = STOP

    def update(self, dt):
        self.sprites.update(dt)
        self.position += self.directions[self.direction] * self.speed * dt

        # direction = self.getValidKey()
        direction = self.pacmanController()

        if self.overshotTarget():
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        else:
            if self.oppositeDirection(direction):
                self.reverseDirection()

    # Returns the direction for Pacman to go
    def pacmanController(self):
        if not self.alive:
            return

        # Update behaviour for pacman to follow
        self.behaviorTree()

        validDirections = self.validDirections()
        direction = self.directionMethod(validDirections)

        return direction

    def behaviorTree(self):
        top_node = Selector(
            [
                Sequence([BerserkMode(self), Kill(self)]),
                Sequence([GhostClose(self), PowerPelletClose(self), GetPowerPellets(self)]),
                Sequence([GhostClose(self), Flee(self)]),
                Sequence([WanderForPellets(self)]),
                Wander(self)
            ]
        )
        top_node.run()

    def getValidKey(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return STOP

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            if self.collideCheck(pellet):
                return pellet
        return None

    def collideGhost(self, ghost):
        return self.collideCheck(ghost)

    def collideCheck(self, other):
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius) ** 2
        if dSquared <= rSquared:
            return True
        return False

    def validDirections(self):
        directions = []
        for key in [UP, DOWN, LEFT, RIGHT]:
            if self.validDirection(key):
                if key != self.direction * -1:
                    directions.append(key)
        if len(directions) == 0:
            directions.append(self.direction * -1)
        return directions

    def closestGhostAndDistance(self):
        closestGhost = None
        closestDistance = 99999
        for i in range(len(self.ghosts)):
            if self.ghosts[i].mode.current == SPAWN:
                continue
            distV = self.position - self.ghosts[i].position
            dist = distV.magnitude()
            if dist < closestDistance:
                closestGhost = self.ghosts[i]
                closestDistance = dist
        return (closestGhost, closestDistance)

    def closestPelletWithDistance(self, powerpellet=False):
        closestPellets = None
        closestDistance = 99999
        pellets = self.pellets
        if powerpellet:
            pellets = self.pp

        for i in range(len(pellets)):
            node = self.nodes.getNodeFromPixels(pellets[i].position.x, pellets[i].position.y)
            if (pellets[i] not in pellets or
                    node is None):
                continue
            distV = self.position - pellets[i].position
            dist = distV.magnitude()
            if dist < closestDistance:
                closestPellets = pellets[i]
                closestDistance = dist
        return closestPellets, closestDistance

    def extractPathTo(self, previous_nodes, source, goal):
        path = []
        node = goal
        cost = 0
        while node != source:
            path.append(node)
            cost = cost + 1
            node = previous_nodes[node]
        path.append(source)
        path.reverse()
        # print(f"Path: {path}")
        return path, cost

    def getGhostDirection(self, directions):
        closest_ghost, distance = self.closestGhostAndDistance()
        ghost_node = self.nodes.getNodeFromPixels(closest_ghost.target.position.x, closest_ghost.target.position.y)
        return self.getDirectionToGoal(directions, ghost_node)

    def getPowerPelletDirection(self, directions):
        closest_powerpellet, distance = self.closestPelletWithDistance(True)
        pp_node = self.nodes.getNodeFromPixels(closest_powerpellet.position.x, closest_powerpellet.position.y)
        return self.getDirectionToGoal(directions, pp_node)

    def getPelletDirection(self, directions):
        closest_pellet, distance = self.closestPelletWithDistance(False)
        pp_node = self.nodes.getNodeFromPixels(closest_pellet.position.x, closest_pellet.position.y)
        direction = self.getDirectionToGoal(directions, pp_node)
        print(f"Chosen wander direction: {direction}")
        return direction

    def getDirectionToGoal(self, directions, goal):
        sourceNode = self.target
        paths_from_pacman = non_fucked_dijkstra(self.nodes, sourceNode)
        path_to_goal, length = self.extractPathTo(paths_from_pacman, sourceNode, goal)
        best_target = path_to_goal[0]
        if len(path_to_goal) > 1:
            best_target = path_to_goal[1]

        for neighborKey in self.target.neighbors.keys():
            if neighborKey in directions:
                neighborNode = self.target.neighbors[neighborKey]
                if neighborNode is not None and neighborNode.position == best_target.position:
                    return neighborKey

        return choice(directions)

    def getDirectionAwayFromGhosts(self, directions, prioritizePellets=False):
        dangerous_directions = self.getGhostTargetDirections(7)

        if self.direction in dangerous_directions:
            rndNm = random.randrange(0, 3)
            if rndNm == 1:
                directions.append(self.direction * -1)

        good_directions = []
        for direction in directions:
            if direction not in dangerous_directions:
                good_directions.append(direction)

        if len(good_directions) == 0:
            print("No good directions to pick")
            return choice(directions)

        print(f"good dirs: {good_directions}")
        print(f"bad dirs: {dangerous_directions}")
        pelletDirection = self.getPelletDirection(directions)
        if pelletDirection in good_directions:
            print("cash money")
            good_directions.append(pelletDirection)  # bigger chance

        return choice(good_directions)

    # Returns pacman's directions to all nodes which ghosts are targeting
    def getGhostTargetDirections(self, path_limit=5):
        # print(f"No. of nodes: {len(self.nodes.getListOfNodesVector())}")

        sourceNode = self.target
        paths_from_pacman = non_fucked_dijkstra(self.nodes, sourceNode)

        dangerous_directions = []

        g, d = self.closestGhostAndDistance()

        for ghost in self.ghosts:
            ghostPosition = ghost.target.position
            # ghostDistanceToTarget = (self.target.position - ghostPosition).magnitudeSquared()
            # pacmanDistanceToTarget = (self.target.position - self.position).magnitudeSquared()
            # print(ghostDistanceToTarget)
            # if ghostDistanceToTarget <= pacmanDistanceToTarget:
            #     if 20000 > pacmanDistanceToTarget:
            #         dangerous_directions.append(self.direction)
            #         print(f"Ghost is closer to target than pacman")
            #         continue

            goalNode = self.nodes.getNodeFromPixels(ghostPosition.x, ghostPosition.y)
            path_to_ghost, length = self.extractPathTo(paths_from_pacman, sourceNode, goalNode)

            pathLength = len(path_to_ghost)
            if pathLength > path_limit:
                continue
            if pathLength < 2:
                dangerous_directions.append(self.direction)
                continue
            else:
                dangerous_neighbor = path_to_ghost[1]

            for neighborKey in self.target.neighbors.keys():
                neighborNode = self.target.neighbors[neighborKey]
                if neighborNode is not None and neighborNode.position == dangerous_neighbor.position:
                    dangerous_directions.append(neighborKey)
                    break

        return dangerous_directions
