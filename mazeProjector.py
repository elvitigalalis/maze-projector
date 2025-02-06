#!/usr/bin/env python3
"""
Maze Drawer
-----------
This script reads a maze from an ASCII text file (formatted like the sample provided),
parses it into a grid of MazeCells (each with boolean walls: north, east, south, west,
and optionally a start (S) or goal (G) marker), and then draws the maze using Pillow.
User input is requested for:
  - The filename of the maze file.
  - The cell side length in pixels.
  - The wall thickness in pixels.

The ASCII file format is expected to have alternating horizontal and vertical wall rows.
For example, for a maze with R rows and C columns, the file has 2*R+1 lines.
- The first line is a horizontal line that begins with an "o" and then has segments of either
  "   " (no wall) or "---" (wall present) between successive "o" characters.
- The next line begins with "|" (or a space) and then, for each cell, has a 3‑character interior
  (which may contain S or G) with vertical walls indicated by "|" between cells.
- These two types of lines alternate, and the last line gives the southern walls.
"""

from PIL import Image, ImageDraw
import sys

# Define a MazeCell class to store wall information and cell marker (start/goal)
class MazeCell:
    def __init__(self):
        self.north = False  # wall on the north side
        self.east  = False  # wall on the east side
        self.south = False  # wall on the south side
        self.west  = False  # wall on the west side
        self.start = False  # True if this cell is marked as the start ('S')
        self.goal  = False  # True if this cell is marked as the goal ('G')

def parse_maze_file(filename):
    """
    Parses the maze text file and returns a 2D list of MazeCells along with the maze dimensions.
    The file is assumed to have 2*maze_rows+1 lines.
    """
    try:
        with open(filename, 'r') as file:
            # Remove newline characters from each line
            lines = [line.rstrip('\n') for line in file if line.strip() != '']
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    total_lines = len(lines)
    if total_lines % 2 == 0:
        raise ValueError("Maze file format error: Expected an odd number of lines.")

    maze_rows = (total_lines - 1) // 2
    # The first horizontal line (which starts with 'o') determines the number of columns.
    # Its length should be: maze_cols * 4 + 1 (each cell has 3 chars for the wall segment plus an "o")
    maze_cols = (len(lines[0]) - 1) // 4

    # Create the maze grid (2D list of MazeCells)
    maze = [[MazeCell() for _ in range(maze_cols)] for _ in range(maze_rows)]

    # For each maze row, parse the horizontal (north/south) and vertical (west/east) wall lines.
    for r in range(maze_rows):
        # Parse the horizontal line above the row (north walls for row r)
        horizontal_top = lines[2 * r]
        for c in range(maze_cols):
            # Each cell segment starts at index c*4+1 and spans 3 characters.
            segment = horizontal_top[c * 4 + 1 : c * 4 + 4]
            maze[r][c].north = (segment == '---')

        # Parse the vertical line that contains cell interiors and west/east walls for row r.
        vertical_line = lines[2 * r + 1]
        for c in range(maze_cols):
            # The west wall character for cell (r, c) is at index c*4.
            west_char = vertical_line[c * 4]
            # The cell interior is 3 characters long.
            cell_interior = vertical_line[c * 4 + 1 : c * 4 + 4]
            # The east wall character for cell (r, c) is right after the interior.
            east_char = vertical_line[c * 4 + 4]
            maze[r][c].west = (west_char == '|')
            maze[r][c].east = (east_char == '|')

            # Check the interior for markers ('S' for start, 'G' for goal)
            cell_marker = cell_interior.strip()
            if cell_marker == 'S':
                maze[r][c].start = True
            elif cell_marker == 'G':
                maze[r][c].goal = True

        # Parse the horizontal line below the row (south walls for row r)
        horizontal_bottom = lines[2 * r + 2]
        for c in range(maze_cols):
            segment = horizontal_bottom[c * 4 + 1 : c * 4 + 4]
            maze[r][c].south = (segment == '---')

    return maze, maze_rows, maze_cols

def draw_maze(maze, maze_rows, maze_cols, cell_size, wall_thickness):
    """
    Draws the maze using Pillow.
    - maze: 2D list of MazeCells.
    - maze_rows, maze_cols: dimensions of the maze.
    - cell_size: side length of each cell in pixels.
    - wall_thickness: thickness of walls in pixels.
    
    Returns a Pillow Image object.
    """
    # Calculate image dimensions. Add wall_thickness to ensure outer walls are fully drawn.
    img_width = maze_cols * cell_size + wall_thickness
    img_height = maze_rows * cell_size + wall_thickness
    image = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(image)

    # First, fill the cells that are marked as start or goal.
    # (You can change the colors as desired.)
    for r in range(maze_rows):
        for c in range(maze_cols):
            x = c * cell_size
            y = r * cell_size
            if maze[r][c].start:
                # Fill start cell with light green.
                draw.rectangle(
                    [x + wall_thickness, y + wall_thickness, x + cell_size, y + cell_size],
                    fill="lightgreen"
                )
            elif maze[r][c].goal:
                # Fill goal cell with light coral.
                draw.rectangle(
                    [x + wall_thickness, y + wall_thickness, x + cell_size, y + cell_size],
                    fill="lightcoral"
                )

    # Now, draw the walls for each cell.
    for r in range(maze_rows):
        for c in range(maze_cols):
            x = c * cell_size
            y = r * cell_size

            # Draw the north wall
            if maze[r][c].north:
                draw.line(
                    [(x, y), (x + cell_size, y)],
                    fill="black",
                    width=wall_thickness
                )
            # Draw the west wall
            if maze[r][c].west:
                draw.line(
                    [(x, y), (x, y + cell_size)],
                    fill="black",
                    width=wall_thickness
                )
            # Draw the east wall
            if maze[r][c].east:
                draw.line(
                    [(x + cell_size, y), (x + cell_size, y + cell_size)],
                    fill="black",
                    width=wall_thickness
                )
            # Draw the south wall
            if maze[r][c].south:
                draw.line(
                    [(x, y + cell_size), (x + cell_size, y + cell_size)],
                    fill="black",
                    width=wall_thickness
                )

    return image

def main():
    # Ask the user for the maze text file name.
    maze_filename = input("Enter the maze file name (e.g., maze.txt): ").strip()
    # Ask for drawing parameters.
    try:
        cell_size = int(input("Enter cell side length in pixels (e.g., 40): ").strip())
        wall_thickness = int(input("Enter wall thickness in pixels (e.g., 4): ").strip())
    except ValueError:
        print("Invalid number entered. Please enter integer values.")
        sys.exit(1)

    # Parse the maze file.
    maze, maze_rows, maze_cols = parse_maze_file(maze_filename)
    print(f"Maze parsed: {maze_rows} rows x {maze_cols} columns.")

    # Draw the maze.
    maze_image = draw_maze(maze, maze_rows, maze_cols, cell_size, wall_thickness)

    # Save the image.
    output_filename = "maze_output.png"
    maze_image.save(output_filename)
    print(f"Maze drawn and saved as '{output_filename}'.")
    # Optionally, display the image.
    maze_image.show()

if __name__ == "__main__":
    main()