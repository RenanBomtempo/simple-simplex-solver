import string

# function to print green text
def green(txt):
    return f"\033[92m{txt}\033[0m"

# function to print red text
def red(txt):
    return f"\033[91m{txt}\033[0m"

# function that recieves a float an prints it to the screen with a color depending on its value
def FloatToColoredString(val, decimals=1):
    txt = f"{val:{decimals+6}.{decimals}f}"
    if val < 0:
       return red(txt)
    elif val > 0:
        return green(txt)
    return txt

def CountAlphanumericWithoutColor(s: str):
    # Create a set of all alphanumeric characters
    alphanumeric = set(string.digits + "|.- ")

    # Replace all color codes with empty strings
    s = s.replace("\033[91m", "")
    s = s.replace("\033[92m", "")
    s = s.replace("\033[0m", "")

    # Use filter to remove non-alphanumeric characters
    alphanumeric_chars = list(filter(lambda ch: ch in alphanumeric, s))

    # Use len to count the number of remaining characters
    return len(alphanumeric_chars)

def MatrixToString(matrix, decimals=1):
    return " |\n".join([" ".join(["|"+FloatToColoredString(val, decimals) for val in row]) for row in matrix]) + " |"

def VectorToString(vector, decimals=1):
    return " ".join(["|"+FloatToColoredString(val, decimals) for val in vector]) + " |"