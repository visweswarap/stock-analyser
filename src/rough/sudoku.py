import random
import time

random.seed(time.time())


def print_sudoku(grid):
    for i, row in enumerate(grid):
        if i > 0 and i % 3 == 0:
            print("-" * 21)  # Separate every 3 rows with a line
        formatted_row = " ".join(map(str, row))
        formatted_row = formatted_row.replace("0", " ")
        print(formatted_row[:5] + " | " + formatted_row[6:11] + " | " + formatted_row[12:])
    print()  # Add an extra line break at the end


def is_valid_move(grid, row, col, num):
    # Check if the number is not present in the current row and column
    if num in grid[row] or num in [grid[i][col] for i in range(9)]:
        return False

    # Check if the number is not present in the 3x3 subgrid
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(start_row, start_row + 3):
        for j in range(start_col, start_col + 3):
            if grid[i][j] == num:
                return False

    return True


def solve_sudoku(grid):
    empty_cell = find_empty_cell(grid)
    if not empty_cell:
        return True  # Puzzle is solved

    row, col = empty_cell
    random_numbers = random.sample(range(1, 10), 9)

    for num in random_numbers:
        if is_valid_move(grid, row, col, num):
            grid[row][col] = num
            if solve_sudoku(grid):
                return True
            grid[row][col] = 0  # Backtrack if the solution is not valid

    return False


def find_empty_cell(grid):
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return i, j
    return None


def generate_sudoku(difficulty_level):
    random.seed(time.time())  # Seed the random number generator with the current system time
    grid = [[0] * 9 for _ in range(9)]
    solve_sudoku(grid)

    # Remove numbers to create the puzzle based on difficulty level
    if difficulty_level == "easy":
        remove_count = 30
    elif difficulty_level == "medium":
        remove_count = 40
    elif difficulty_level == "hard":
        remove_count = 50
    else:
        raise ValueError("Invalid difficulty level")

    # Remove numbers from the solved grid
    for _ in range(remove_count):
        row, col = random.randint(0, 8), random.randint(0, 8)
        while grid[row][col] == 0:
            row, col = random.randint(0, 8), random.randint(0, 8)
        grid[row][col] = 0

    return grid


if __name__ == "__main__":
    difficulty_level = "medium"
    sudoku_puzzle = generate_sudoku(difficulty_level)
    print("Generated Sudoku Puzzle (Difficulty Level: {}):".format(difficulty_level.capitalize()))
    print_sudoku(sudoku_puzzle)
