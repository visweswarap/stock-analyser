import time

# Define patterns for each character
logo_patterns = {
    'P': [
        "#### ",
        "#   #",
        "#   #",
        "#### ",
        "#    ",
        "#    ",
        "#    ",
    ],
    'E': [
        "####",
        "#   ",
        "#   ",
        "####",
        "#   ",
        "#   ",
        "####",
    ],
    'A': [
        " ###  ",
        "#   # ",
        "#   # ",
        "##### ",
        "#   # ",
        "#   # ",
        "#   # ",
    ],
    'L': [
        "#    ",
        "#    ",
        "#    ",
        "#    ",
        "#    ",
        "#    ",
        "#### ",
    ]
}


# Function to print the logo
def print_logo(word):
    for i in range(7):  # 5 rows for each character
        for char in word:
            pattern = logo_patterns.get(char.upper(), [" " * 7])
            print(pattern[i], end="  ")
        print()  # Move to the next row
        time.sleep(0.5)  # Add a small delay to create a blinking effect


if __name__ == "__main__":
    word_to_print = "PEPALA"
    print_logo(word_to_print)
