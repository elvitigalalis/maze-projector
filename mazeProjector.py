import pygame
import sys

# Define a simple MazeCell class to hold wall information and any marker.
class MazeCell:
    def __init__(self):
        self.north = False
        self.south = False
        self.east = False
        self.west = False
        self.marker = None  # e.g., "S" or "G"

def parse_ascii_maze(filename):
    """
    Parses an ASCII maze file formatted as follows:
    
    - The file should have 2*rows + 1 lines (for a 16×16 maze, 33 lines).
    - Even-indexed lines (0, 2, 4, …) are horizontal boundary lines.
      These lines consist of alternating "o" (vertices) and 3-character segments.
      A segment of '---' indicates a wall; a segment of '   ' (three spaces) indicates no wall.
    - Odd-indexed lines are the vertical wall lines.
      They have a pattern of 4-character blocks: the first and fourth characters are
      vertical boundaries ('|' indicates a wall, a space indicates no wall), and the two
      middle characters (or three characters if you include the extra space) represent
      the interior of the cell. If a cell interior contains an 'S' or 'G' (possibly padded by spaces),
      that marker is recorded.
      
    Returns a 16×16 grid (list of lists) of MazeCell objects.
    """
    rows, cols = 16, 16
    expected_lines = 2 * rows + 1  # 33 lines for a 16x16 maze

    with open(filename, 'r') as f:
        # Remove newline characters.
        lines = [line.rstrip("\n") for line in f.readlines()]

    if len(lines) < expected_lines:
        print("Error: Maze file has fewer than expected lines.")
        sys.exit(1)

    # Create the grid of MazeCell objects.
    grid = [[MazeCell() for _ in range(cols)] for _ in range(rows)]
    
    # Each horizontal boundary line is expected to be 4*cols + 1 characters long.
    # For each cell, we will extract:
    # - North wall from the horizontal line at index (2*r)
    # - South wall from the horizontal line at index (2*r + 2)
    # - West and East walls from the vertical line at index (2*r + 1)
    # - Marker from the interior substring of the vertical line.
    for r in range(rows):
        top_line = lines[2 * r]
        vertical_line = lines[2 * r + 1]
        bottom_line = lines[2 * r + 2] if (2 * r + 2) < len(lines) else None

        for c in range(cols):
            # Calculate the starting index of the 4-character block for cell (r, c).
            block_start = 4 * c
            # For horizontal segments, the wall indicator is found in the substring starting at index (block_start + 1) with length 3.
            segment_top = top_line[block_start + 1: block_start + 4]
            if segment_top == "---":
                grid[r][c].north = True
            if bottom_line:
                segment_bottom = bottom_line[block_start + 1: block_start + 4]
                if segment_bottom == "---":
                    grid[r][c].south = True

            # For vertical walls, the left (west) wall is at the beginning of the block.
            if vertical_line[block_start] == '|':
                grid[r][c].west = True
            # The right (east) wall is at index block_start + 4.
            if vertical_line[block_start + 4] == '|':
                grid[r][c].east = True

            # The interior of the cell is in the substring from (block_start + 1) to (block_start + 4).
            interior = vertical_line[block_start + 1: block_start + 4].strip()
            if interior in ['S', 'G']:
                grid[r][c].marker = interior

    return grid

def draw_maze(screen, grid, cell_size):
    """
    Draws the maze onto the Pygame screen.
    For each cell, if a wall exists on a side, a line is drawn.
    If the cell contains a marker (S or G), it is rendered in the cell's center.
    """
    wall_color = (255, 255, 255)    # White for walls.
    marker_color = (255, 0, 0)      # Red for markers.
    bg_color = (0, 0, 0)            # Black background.
    
    screen.fill(bg_color)
    rows = len(grid)
    cols = len(grid[0])
    
    # Draw walls for each cell.
    for r in range(rows):
        for c in range(cols):
            x = c * cell_size
            y = r * cell_size

            # Draw north wall.
            if grid[r][c].north:
                pygame.draw.line(screen, wall_color, (x, y), (x + cell_size, y), 2)
            # Draw south wall.
            if grid[r][c].south:
                pygame.draw.line(screen, wall_color, (x, y + cell_size), (x + cell_size, y + cell_size), 2)
            # Draw west wall.
            if grid[r][c].west:
                pygame.draw.line(screen, wall_color, (x, y), (x, y + cell_size), 2)
            # Draw east wall.
            if grid[r][c].east:
                pygame.draw.line(screen, wall_color, (x + cell_size, y), (x + cell_size, y + cell_size), 2)
            
            # If there is a marker, draw it centered in the cell.
            if grid[r][c].marker:
                font = pygame.font.SysFont("Arial", cell_size // 2)
                text_surface = font.render(grid[r][c].marker, True, marker_color)
                text_rect = text_surface.get_rect(center=(x + cell_size/2, y + cell_size/2))
                screen.blit(text_surface, text_rect)
    
    pygame.display.flip()

def main():
    if len(sys.argv) < 3:
        print("Usage: python ascii_maze_projector.py <maze_file.txt> <cell_size>")
        print("Example: python ascii_maze_projector.py maze.txt 40")
        sys.exit(1)

    maze_file = sys.argv[1]
    try:
        cell_size = int(sys.argv[2])
    except ValueError:
        print("Error: <cell_size> must be an integer.")
        sys.exit(1)
    
    # Parse the ASCII maze into a grid of MazeCell objects.
    grid = parse_ascii_maze(maze_file)
    
    pygame.init()
    window_size = (16 * cell_size, 16 * cell_size)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("ASCII Maze Projector")
    
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        draw_maze(screen, grid, cell_size)
        clock.tick(30)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()