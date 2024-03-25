import sys

from dataclasses import dataclass, field
from typing import Any
from queue import PriorityQueue

@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any=field(compare=False)

# Shortest path from source to every other node
def non_fucked_dijkstra(nodes, start_node):
    distTo = {}
    prevNode = {}
    max_value = sys.maxsize

    for node in nodes.nodesLUT.values():
        distTo[node] = max_value
        prevNode[node] = None
    distTo[start_node] = 0.0

    pq = PriorityQueue()
    pq.put(PrioritizedItem(0.0, start_node))

    while(pq.qsize() != 0):
        #print(pq.qsize())
        popped = pq.get()
        v = popped.item
        neighs = nodes.get_real_neighbors(v)
        for w in neighs:
            length = (w.position - v.position).magnitudeSquared()
            #print(f"v: {v}, w: {w}")
            if(distTo[w] > distTo[v] + length):
                #print(f"dist to w: {distTo[w]}, to v: {distTo[v]}, lenght beteen: {length}")
                distTo[w] = distTo[v] + length
                prevNode[w] = v
                pq.put(PrioritizedItem(distTo[w], w)) # not optimal

    return prevNode

def dijkstra(nodes, start_node):
    unvisited_nodes = list(nodes.costs)
    shortest_path = {}
    previous_nodes = {}

    max_value = sys.maxsize
    for node in unvisited_nodes:
        shortest_path[node] = max_value
    shortest_path[start_node] = 0

    while unvisited_nodes:
        current_min_node = None
        for node in unvisited_nodes:
            if current_min_node is None:
                current_min_node = node
            elif shortest_path[node] < shortest_path[current_min_node]:
                current_min_node = node

        neighbors = nodes.getNeighbors(current_min_node)
        for neighbor in neighbors:
            tentative_value = (
                shortest_path[current_min_node] + 1
            )  # nodes.value(current_min_node, neighbor)
            if tentative_value < shortest_path[neighbor]:
                shortest_path[neighbor] = tentative_value
                # We also update the best path to the current node
                previous_nodes[neighbor] = current_min_node

        # After visiting its neighbors, we mark the node as "visited"
        unvisited_nodes.remove(current_min_node)

    return previous_nodes, shortest_path


def print_result(previous_nodes, shortest_path, start_node, target_node):
    path = []
    node = target_node

    while node != start_node:
        path.append(node)
        node = previous_nodes[node]

    # Add the start node manually
    path.append(start_node)

    print(
        "We found the following best path with a value of {}.".format(
            shortest_path[target_node]
        )
    )
    print(path)


#########
# A*
def heuristic(node1, node2):
    # manhattan distance
    return abs(node1[0] - node2[0]) + abs(node1[1] - node2[1])


def dijkstra_or_a_star(nodes, start_node, a_star=False):
    unvisited_nodes = list(nodes.costs)
    shortest_path = {}
    previous_nodes = {}

    max_value = sys.maxsize
    for node in unvisited_nodes:
        shortest_path[node] = max_value
    shortest_path[start_node] = 0

    while unvisited_nodes:
        current_min_node = None
        for node in unvisited_nodes:
            if current_min_node is None:
                current_min_node = node
            elif shortest_path[node] < shortest_path[current_min_node]:
                current_min_node = node

        neighbors = nodes.getNeighbors(current_min_node)

        #print(f"Min mode = {current_min_node}")
        #print(f" nei = {neighbors}")

        for neighbor in neighbors:
            if a_star:
                tentative_value = shortest_path[current_min_node] + heuristic(
                    current_min_node, neighbor
                )
            else:
                tentative_value = shortest_path[current_min_node] + 1
            try:
                if tentative_value < shortest_path[neighbor]:
                    shortest_path[neighbor] = tentative_value
                    # We also update the best path to the current node
                    previous_nodes[neighbor] = current_min_node
            except:
                print("whoops")

        # After visiting its neighbors, we mark the node as "visited"
        unvisited_nodes.remove(current_min_node)
    return previous_nodes, shortest_path
