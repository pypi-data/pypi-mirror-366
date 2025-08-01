import os
import sys

if os.name == "nt":
    os.system('')

try: ESC = "\033"
except: ESC = "\x1b"

RESET   = f"{ESC}[0m"

# BASIC
BLACK   = f"{ESC}[0;30m"
RED     = f"{ESC}[0;31m"
GREEN   = f"{ESC}[0;32m"
YELLOW  = f"{ESC}[0;33m"
BLUE    = f"{ESC}[0;34m"
PURPLE  = f"{ESC}[0;35m"
CYAN    = f"{ESC}[0;36m"
WHITE   = f"{ESC}[0;37m"

# BOLD
BOLD_BLACK   = f"{ESC}[1;30m"
BOLD_RED     = f"{ESC}[1;31m"
BOLD_GREEN   = f"{ESC}[1;32m"
BOLD_YELLOW  = f"{ESC}[1;33m"
BOLD_BLUE    = f"{ESC}[1;34m"
BOLD_PURPLE  = f"{ESC}[1;35m"
BOLD_CYAN    = f"{ESC}[1;36m"
BOLD_WHITE   = f"{ESC}[1;37m"

# UNDERLINE
UNDERLINE_BLACK   = f"{ESC}[4;30m"
UNDERLINE_RED     = f"{ESC}[4;31m"
UNDERLINE_GREEN   = f"{ESC}[4;32m"
UNDERLINE_YELLOW  = f"{ESC}[4;33m"
UNDERLINE_BLUE    = f"{ESC}[4;34m"
UNDERLINE_PURPLE  = f"{ESC}[4;35m"
UNDERLINE_CYAN    = f"{ESC}[4;36m"
UNDERLINE_WHITE   = f"{ESC}[4;37m"

# BACKGROUND
BG_BLACK   = f"{ESC}[40m"
BG_RED     = f"{ESC}[41m"
BG_GREEN   = f"{ESC}[42m"
BG_YELLOW  = f"{ESC}[43m"
BG_BLUE    = f"{ESC}[44m"
BG_PURPLE  = f"{ESC}[45m"
BG_CYAN    = f"{ESC}[46m"
BG_WHITE   = f"{ESC}[47m"

# CLASSES

# BASIC
class Basic:
    def __init__(self) -> None:
        self.BLACK = BLACK
        self.RED = RED
        self.GREEN = GREEN
        self.YELLOW = YELLOW
        self.BLUE = BLUE
        self.PURPLE = PURPLE
        self.CYAN = CYAN
        self.WHITE = WHITE
BASIC = Basic()

# BOLD
class Bold:
    def __init__(self) -> None:
        self.BLACK = BOLD_BLACK
        self.RED = BOLD_RED
        self.GREEN = BOLD_GREEN
        self.YELLOW = BOLD_YELLOW
        self.BLUE = BOLD_BLUE
        self.PURPLE = BOLD_PURPLE
        self.CYAN = BOLD_CYAN
        self.WHITE = BOLD_WHITE
BOLD = Bold()

# BOLD
class Underline:
    def __init__(self) -> None:
        self.BLACK = UNDERLINE_BLACK
        self.RED = UNDERLINE_RED
        self.GREEN = UNDERLINE_GREEN
        self.YELLOW = UNDERLINE_YELLOW
        self.BLUE = UNDERLINE_BLUE
        self.PURPLE = UNDERLINE_PURPLE
        self.CYAN = UNDERLINE_CYAN
        self.WHITE = UNDERLINE_WHITE
UNDERLINE = Underline()

# BACKGROUND
class Background:
    def __init__(self) -> None:
        self.BLACK = BG_BLACK
        self.RED = BG_RED
        self.GREEN = BG_GREEN
        self.YELLOW = BG_YELLOW
        self.BLUE = BG_BLUE
        self.PURPLE = BG_PURPLE
        self.CYAN = BG_CYAN
        self.WHITE = BG_WHITE
BACKGROUND = Background()

# ALL
class All:
    def __init__(self) -> None:
        self.BASIC = BASIC
        self.BOLD = BOLD
        self.UNDERLINE = UNDERLINE
        self.BACKGROUND = BACKGROUND
ALL = All()