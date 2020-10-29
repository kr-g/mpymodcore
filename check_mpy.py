import sys

"""
http://docs.micropython.org/en/v1.12/reference/mpyfiles.html
"""


def print_mp_info():
    sys_mpy = sys.implementation.mpy
    arch = [
        None,
        "x86",
        "x64",
        "armv6",
        "armv6m",
        "armv7m",
        "armv7em",
        "armv7emsp",
        "armv7emdp",
        "xtensa",
        "xtensawin",
    ][sys_mpy >> 10]
    print("mpy version:", sys_mpy & 0xFF)
    print("mpy flags:", end="")
    if arch:
        print(" -march=" + arch, end="")
    if sys_mpy & 0x100:
        print(" -mcache-lookup-bc", end="")
    if not sys_mpy & 0x200:
        print(" -mno-unicode", end="")
    print()


try:
    import os

    MPY_FILE = os.path.join("mpy", "modcore", "__init__.mpy")
    MPY_FILE_DEV = os.path.join("modcore", "__init__.mpy")
except:
    print("running on micropython?")
    MPY_FILE = "modcore/__init__.mpy"


def print_mpy_info(fnam=MPY_FILE):
    with open(fnam, "rb") as f:
        ver = f.read(2)
        features = f.read(1)
        bits_small_int = f.read(1)
        print(ver, features, bits_small_int, ord(bits_small_int))
