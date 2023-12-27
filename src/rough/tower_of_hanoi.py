count = 0
disks = 6

def tower_of_hanoi(n, source, target, auxiliary, moves=[]):
    if n == 1:
        moves.append((source, target))
    else:
        tower_of_hanoi(n-1, source, auxiliary, target, moves)
        moves.append((source, target))
        tower_of_hanoi(n-1, auxiliary, target, source, moves)


def print_hanoi_state(moves):
    global count
    pegs = {1: list(range(1, number_of_disks+1)), 2: [], 3: []}

    for move in moves:
        disk = pegs[move[0]].pop() if pegs[move[0]] else None
        if disk:
            pegs[move[1]].append(disk)
        print(pegs)
        count = count+1

    for peg in sorted(pegs.keys()):
        print(f"Peg {peg}: {pegs[peg]}")


if __name__ == "__main__":
    number_of_disks = 8
    disks = number_of_disks
    source_peg, target_peg, auxiliary_peg = 1, 3, 2

    hanoi_moves = []
    tower_of_hanoi(number_of_disks, source_peg, target_peg, auxiliary_peg, hanoi_moves)

    # Initialize the first peg with disks 1 to 6
    print("Initial state:")
    print_hanoi_state([(source_peg, source_peg)] * (number_of_disks - 1))

    print(f"\nTower of Hanoi with {number_of_disks} disks:")
    print_hanoi_state(hanoi_moves)
    print(f"Total moves: {count}")
