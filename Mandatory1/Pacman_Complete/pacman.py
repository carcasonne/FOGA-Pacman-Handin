import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
from behaviourTree import *
from random import randint, choice

class Pacman(Entity):
    def __init__(self, node):
        Entity.__init__(self, node)
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        # Ghosts and pacman have recursive constructors
        self.ghosts = None

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
        self.position += self.directions[self.direction]*self.speed*dt


        #direction = self.getValidKey()
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
        # Update behaviour for pacman to follow
        self.behaviorTree()
        
        validDirections = self.validDirections()
        direction = self.directionMethod(validDirections)
        
        return direction

    def behaviorTree(self):
        top_node = Selector(
            [
                Sequence([GhostClose(self), Flee(self)]),
                Wander(self)
            ]
        )
        
        top_node.run()
    
      # def behaviorTree(self):
      #  top_node = Selector(
      #      [
      #          Sequence([GhostClose(self), Flee(self)]),
      #          Sequence([HaveFruit(self), SeekNearestEnemy(self)]),
      #          Sequence([FruitCloseAndDanger(self), SeekFruit(self)]),
      ##          SeekPellet(self)
       #     ]
       # )
      #  
      #  top_node.run()
    
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
        rSquared = (self.collideRadius + other.collideRadius)**2
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
            distV = self.position - self.ghosts[i].position
            dist = distV.magnitude()
            if dist < closestDistance:
                closestGhost = self.ghosts[i]
                closestDistance = dist
        return (closestGhost, closestDistance)