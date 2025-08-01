import re
import sys

VERSION = "0.1.0.dev3"


def get_version(naked=False):
    if naked:
        return re.split("(a|b|rc|.dev)", VERSION)[0]
    return VERSION


def get_full_version(program=None, naked=False):
    program = f"{program or ''} {get_version(naked)}".strip()
    interpreter = f"{get_interpreter()} {sys.version.split()[0]}"
    return f"{program} ({interpreter} on {sys.platform})"


def get_interpreter():
    if "PyPy" in sys.version:
        return "PyPy"
    return "Python"
