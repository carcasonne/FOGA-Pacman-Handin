from __future__ import annotations

# avoiding circular dependency
from genericpath import exists
import os
from telnetlib import DO
from typing import TYPE_CHECKING, Any
from enum import IntEnum
import pickle
import random

import pygame
# from scipy import constants
from constants import (
    SCATTER,
    FREIGHT,
)

from vector import Vector2
from run import GameController
from constants import UP, DOWN, RIGHT, LEFT


class State_old:
    def __init__(self, playerPosition: Vector2) -> None:
        self.playerPosition = playerPosition.asTuple()

    def __str__(self) -> str:
        return "{}.{}".format(self.playerPosition[0], self.playerPosition[1])


def myRound(x, base=5):
    return int(base * round(float(x)/base))

# State represented as: pacmanPosition, distance to each ghost, distance to each power pellet
class State:
    def __init__(self, playerPosition, targetPosition: Vector2, ghostPositions, ppPositions) -> None:
        self.playerPosition = playerPosition
        self.targetPosition = targetPosition
        self.ghostPositions = ghostPositions
        self.powerPelletPositions = ppPositions

    def __str__(self) -> str:
        strrep = "{};{}".format(int(self.targetPosition.x), int(self.targetPosition.y))
        closestGhost = {
            "ghost": None,
            "distance": 99999999999,
        }
        for ghost in self.ghostPositions:
            dist = myRound((self.playerPosition - ghost.position).magnitudeSquared(), 100)
            if dist < closestGhost["distance"]:
                closestGhost["ghost"] = ghost
                closestGhost["distance"] = dist
        strrep += f";{closestGhost['distance']};{closestGhost['ghost'].mode.current == FREIGHT}"

        closestPP = {
            "pp": None,
            "distance": 99999999999,
        }
        for pp in self.powerPelletPositions:
            dist = myRound(round((self.playerPosition - pp.position).magnitudeSquared()), 300)
            if dist < closestPP["distance"]:
                closestPP["pp"] = pp
                closestPP["distance"] = dist
        strrep += f";{closestPP['distance'] < 5000}"

        # print(strrep)
        return strrep


class Action(IntEnum):
    UP = UP
    DOWN = DOWN
    LEFT = LEFT
    RIGHT = RIGHT

    def __str__(self) -> str:
        return str(self)


def hash(state: State, action: Action) -> str:
    return "{}.{}".format(str(state), str(action))


class QValueStore:
    def __init__(self, filePath: str) -> None:
        self.filePath = filePath
        self.storage: dict[str, float] = {}
        self.load(self.filePath)

    def getQValue(self, state: State, action: Action) -> float:
        h = hash(state, action)
        value = self.storage.get(h)
        if value:
            return value
        else:
            return 0.0

    def getBestAction(self, state: State, possibleActions: list[Action]) -> Action:
        return max(possibleActions, key=lambda action: self.getQValue(state, action))

    def storeQValue(self, state: State, action: Action, value: float):
        h = hash(state, action)
        self.storage[h] = value

    def save(self):
        print("Saving: dictionary size", len(self.storage))
        fw = open(self.filePath, "wb")
        pickle.dump(self.storage, fw)
        fw.close()

    # Loads a Q-table.
    def load(self, file: str):
        if os.path.exists(file):
            fr = open(file, "rb")
            self.storage = pickle.load(fr)
            print("Loading: dictionary size", len(self.storage))
            fr.close()
        else:
            self.save()


class ReinforcementProblem:
    def __init__(self) -> None:
        self.game = GameController()
        self.game.restartGameRandom()

    def getCurrentState(self) -> State:
        return State(self.game.pacman.position, self.game.pacman.target.position, self.game.ghosts, self.game.pellets.powerpellets)

    # Choose a random starting state for the problem.
    def getRandomState(self) -> State:
        self.game.setPacmanInRandomPosition()
        return self.getCurrentState()

    # Get the available actions for the given state.
    def getAvailableActions(self, state: State) -> list[Action]:
        directions = self.game.pacman.validDirections()

        def intDirectionToString(dir: Action) -> str:
            match dir:
                case Action.UP:
                    return "UP"
                case Action.DOWN:
                    return "DOWN"
                case Action.LEFT:
                    return "LEFT"
                case Action.RIGHT:
                    return "RIGHT"
                case _:
                    return "INV"

        # print(list(map(intDirectionToString, directions)))
        return directions

    def updateGameNTimes(self, frames: int):
        for i in range(frames):
            self.game.update()

    def updateGameForSeconds(self, seconds: float):
        durationMills: float = seconds * 1000
        currentTime = pygame.time.get_ticks()
        endTime = currentTime + durationMills
        while currentTime < endTime:
            self.game.update()
            currentTime = pygame.time.get_ticks()

    # Take the given action and state, and return
    # a pair consisting of the reward and the new state.
    def takeAction(self, state: State, action: Action) -> tuple[float, State]:
        previousScore = self.game.score
        previousLives = self.game.lives
        self.game.pacman.learntDirection = action
        self.updateGameForSeconds(0.1)
        scatteredGhosts = 0
        for ghost in self.game.ghosts:
            if ghost.mode.current == SCATTER:
                scatteredGhosts += 1

        # Please don't die Pacman :(
        lifePenalty = (previousScore - self.game.lives) * 1000

        reward = self.game.score - previousScore + scatteredGhosts * 200 - lifePenalty
        newState = self.getCurrentState()
        return reward, newState

    # PARAMETERS:
    # Learning Rate
    # controls how much influence the current feedback value has over the stored Q-value.

    # Discount Rate
    # how much an action’s Q-value depends on the Q-value at the state (or states) it leads to.

    #  Randomness of Exploration
    # how often the algorithm will take a random action, rather than the best action it knows so far.

    # The Length of Walk
    # number of iterations that will be carried out in a sequence of connected actions.


# Updates the store by investigating the problem.
def QLearning(
        problem: ReinforcementProblem,
        iterations,
        learningRate,
        discountRate,
        explorationRandomness,
        walkLength,
):
    # Get a starting state.
    state = problem.getRandomState()
    saveIterations = 50
    # Repeat a number of times.
    for i in range(iterations):
        if i % saveIterations == 0:
            print("Saving at iteration:", i)
            store.save()
        # Pick a new state every once in a while.
        # if random.uniform(0, 1) < walkLength:
        #     state = problem.getRandomState()

        # Get the list of available actions.
        actions = problem.getAvailableActions(state)

        # Should we use a random action this time?
        if random.uniform(0, 1) < explorationRandomness:
            action = random.choice(actions)
        # Otherwise pick the best action.
        else:
            action = store.getBestAction(state, problem.getAvailableActions(state))

        # Carry out the action and retrieve the reward and new state.
        reward, newState = problem.takeAction(state, action)

        # Get the current q from the store.
        q = store.getQValue(state, action)

        # Get the q of the best action from the new state
        maxQ = store.getQValue(
            newState,
            store.getBestAction(newState, problem.getAvailableActions(newState)),
        )

        # Perform the q learning.
        q = (1 - learningRate) * q + learningRate * (reward + discountRate * maxQ)

        # Store the new Q-value.
        store.storeQValue(state, action, q)
        # And update the state.
        state = newState


if __name__ == "__main__":
    # The store for Q-values, we use this to make decisions based on
    # the learning.
    store = QValueStore("training")
    problem = ReinforcementProblem()

    QLearning(problem, 10000000000, 0.7, 0.75, 0.2, 0.01)
