color_codes = {
    "white": "\033[97m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "green": "\033[92m",
    "pink": "\033[95m",
    "blue": "\033[94m",}

def print_colored(text, color):
    color_code = color_codes.get(color, "\033[97m")  
    print(f"{color_code}{text}\033[0m")