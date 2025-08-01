from fastcolors import *

def basic_colors():
    for color_name in ["BLACK", "RED", "GREEN", "YELLOW", "BLUE", "PURPLE", "CYAN", "WHITE"]:
        color = globals()[color_name]
        print(f"{color}{color_name}{RESET}")

def bold_colors():
    for color_name in ["BOLD_BLACK", "BOLD_RED", "BOLD_GREEN", "BOLD_YELLOW", "BOLD_BLUE", "BOLD_PURPLE", "BOLD_CYAN", "BOLD_WHITE"]:
        color = globals()[color_name]
        print(f"{color}{color_name}{RESET}")

def underline_colors():
    for color_name in ["UNDERLINE_BLACK", "UNDERLINE_RED", "UNDERLINE_GREEN", "UNDERLINE_YELLOW", "UNDERLINE_BLUE", "UNDERLINE_PURPLE", "UNDERLINE_CYAN", "UNDERLINE_WHITE"]:
        color = globals()[color_name]
        print(f"{color}{color_name}{RESET}")

def bg_colors():
    for color_name in ["BG_BLACK", "BG_RED", "BG_GREEN", "BG_YELLOW", "BG_BLUE", "BG_PURPLE", "BG_CYAN", "BG_WHITE"]:
        color = globals()[color_name]
        print(f"{color}{color_name}{RESET}")

bg_colors()