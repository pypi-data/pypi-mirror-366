"""
Test file containing various searching algorithms for algorithm detection testing.
"""

def linear_search(arr, target):
    """Linear search implementation."""
    for i, element in enumerate(arr):
        if element == target:
            return i
    return -1

def binary_search(arr, target):
    """Binary search implementation."""
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

def depth_first_search(graph, start, visited=None):
    """Depth-first search implementation."""
    if visited is None:
        visited = set()
    
    visited.add(start)
    print(start, end=' ')
    
    for neighbor in graph[start]:
        if neighbor not in visited:
            depth_first_search(graph, neighbor, visited)

def breadth_first_search(graph, start):
    """Breadth-first search implementation."""
    visited = set()
    queue = [start]
    visited.add(start)
    
    while queue:
        vertex = queue.pop(0)
        print(vertex, end=' ')
        
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

def dijkstra_algorithm(graph, start):
    """Dijkstra's shortest path algorithm."""
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    unvisited = set(graph.keys())
    
    while unvisited:
        current = min(unvisited, key=lambda node: distances[node])
        
        if distances[current] == float('infinity'):
            break
        
        unvisited.remove(current)
        
        for neighbor, weight in graph[current].items():
            distance = distances[current] + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
    
    return distances 