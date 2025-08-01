from collections import deque # Import deque for efficient queue operations in BFS

def solve_maze(maze, start, end, char_map, start_char='S', end_char='E'):
    # Find start and end coordinates if they are provided as characters instead of tuples
    if isinstance(start, str):
        start_char_to_find = start
        start = None
        for r in range(maze.shape[0]):
            for c in range(maze.shape[1]):
                if maze[r, c] == start_char_to_find:
                    start = (r, c)
                    break # Exit inner loop once start is found
            if start:
                break # Exit outer loop once start is found

    if isinstance(end, str):
        end_char_to_find = end
        end = None
        for r in range(maze.shape[0]):
            for c in range(maze.shape[1]):
                if maze[r, c] == end_char_to_find:
                    end = (r, c)
                    break # Exit inner loop once end is found
            if end:
                break # Exit outer loop once end is found

    # If start or end points were not found in the maze, return an error message and empty results
    if start is None or end is None:
        print("Error: Start or end point not found in the maze.")
        return [], 0, 0

    # Define the Breadth-First Search (BFS) function
    def bfs(allow_soft_obstacles):
        # Initialize a queue for BFS, starting with the start point and its path
        queue = deque([(start, [start])])
        # Keep track of visited cells to avoid infinite loops
        visited = {start}

        # Perform BFS until the queue is empty
        while queue:
            # Get the current cell and its path from the left of the queue
            (y, x), path = queue.popleft()

            # If the current cell is the end point, we've found a solution
            if (y, x) == end:
                steps = len(path) - 1 # Calculate the number of steps (excluding the start)
                soft_obstacles_stepped_on = 0
                # Count the number of soft obstacles in the solution path
                if 'soft_obstacle' in char_map:
                    for (r, c) in path:
                        if maze[r, c] == char_map['soft_obstacle']:
                            soft_obstacles_stepped_on += 1
                return path, steps, soft_obstacles_stepped_on # Return the solution path and metrics

            # Explore possible moves (up, down, left, right) from the current cell
            for move_y, move_x in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                next_y, next_x = y + move_y, x + move_x

                # Check if the next cell is within the maze boundaries and hasn't been visited
                if (0 <= next_y < maze.shape[0] and
                        0 <= next_x < maze.shape[1] and
                        (next_y, next_x) not in visited):

                    cell = maze[next_y, next_x]
                    # Determine if the cell is a path, soft obstacle, start, or end cell
                    is_path = cell == char_map['path']
                    is_soft_obstacle = 'soft_obstacle' in char_map and cell == char_map['soft_obstacle']
                    # Also consider start/end characters as traversable during the search
                    is_start_or_end = cell == start_char if isinstance(start, str) else False
                    is_end_char = cell == end_char if isinstance(end, str) else False

                    # Check if the cell is traversable based on the 'allow_soft_obstacles' flag
                    if is_path or (allow_soft_obstacles and is_soft_obstacle) or cell == start_char or cell == end_char:
                        visited.add((next_y, next_x)) # Mark the cell as visited
                        # Add the next cell and the updated path to the queue
                        queue.append(((next_y, next_x), path + [(next_y, next_x)]))
        # If the queue is empty and the end hasn't been reached, no solution exists
        return [], 0, 0

    # First pass: Try to find a path without crossing soft obstacles
    solution, steps, soft_obstacles = bfs(allow_soft_obstacles=False)
    if solution:
        return solution, steps, soft_obstacles # Return the solution if found

    # Second pass (fallback): If no path is found in the first pass, allow crossing soft obstacles
    return bfs(allow_soft_obstacles=True)