import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
def visualize_maze(maze, char_map, solution=None, start=None, end=None):

    #find start and end coordinates if provided as characters
    if isinstance(start, str):
        start_char = start
        start = None
        for r in range(maze.shape[0]):
            for c in range(maze.shape[1]):
                if maze[r, c] == start_char:
                    start = (r, c)
                    break # Exit inner loop once start is found
            if start:
                break # Exit outer loop once start is found

    if isinstance(end, str):
        end_char = end
        end = None
        for r in range(maze.shape[0]):
            for c in range(maze.shape[1]):
                if maze[r, c] == end_char:
                    end = (r, c)
                    break # Exit inner loop once end is found
            if end:
                break # Exit outer loop once end is found

    #mapping characters in the maze to integer values for plotting
    # This allows us to represent different maze elements numerically
    char_to_val = {
        char_map['path']: 0,
        char_map['wall']: 1,
        char_map['obstacle']: 2,
        char_map['soft_obstacle']: 3,
    }

    # Define a list of colors to be used for visualizing different maze elements
    # The order corresponds to the integer values in val_map
    colors = ['lightgray', 'black', 'darkred', 'orange', 'cyan', 'green', 'blue', 'yellow']

    # Define a mapping from element types to integer values for consistent visualization
    val_map = {
        'path': 0,
        'wall': 1,
        'obstacle': 2,
        'soft_obstacle': 3,
        'solution': 4, # Color for the solution path
        'start': 5,    # Color for the starting point
        'end': 6,      # Color for the ending point
        'solution_on_soft_obstacle': 7 # Special color for solution path on a soft obstacle
    }


    # Convert the character-based maze into a numerical representation for the heatmap
    numeric_maze = np.zeros(maze.shape, dtype=float)
    for r in range(maze.shape[0]):
        for c in range(maze.shape[1]):
            char = maze[r, c]
            # Assign numerical value based on the character, defaulting to 'path' if character not in map
            numeric_maze[r, c] = char_to_val.get(char, val_map['path'])


    # If a solution path is provided, mark the solution cells on the numerical maze
    if solution:
        for (y, x) in solution:
            # Don't overwrite start and end points if they are part of the solution path
            if (y, x) != start and (y, x) != end:
                # Check if the solution path cell is a soft obstacle and assign the special color
                if maze[y, x] == char_map.get('soft_obstacle'):
                    numeric_maze[y, x] = val_map['solution_on_soft_obstacle']
                else:
                    # Otherwise, assign the regular solution color
                    numeric_maze[y, x] = val_map['solution']

    # Mark the start and end points on the numerical maze with their specific colors
    if start:
        numeric_maze[start] = val_map['start']

    if end:
        numeric_maze[end] = val_map['end']

    # Create a colormap and normalization for the heatmap based on the defined colors and values
    cmap = plt.cm.colors.ListedColormap(colors)
    bounds = np.arange(-0.5, len(colors) + 0.5, 1)
    norm = plt.cm.colors.BoundaryNorm(bounds, cmap.N)

    # Create the heatmap visualization of the numerical maze
    plt.figure(figsize=(8, 8))
    sns.heatmap(numeric_maze, cmap=cmap, norm=norm, cbar=False, linewidths=0.5, linecolor='black')
    plt.xticks([]) # Hide x-axis ticks
    plt.yticks([]) # Hide y-axis ticks
    plt.show() # Display the plot