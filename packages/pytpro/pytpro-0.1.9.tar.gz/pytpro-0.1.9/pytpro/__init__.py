from .main import (
    # Web
    htmlcssjs, image,

    # Core UI
    write, title, header, subheader, caption,

    # Alert Boxes
    alertbox_red, alertbox_green, alertbox_blue, alertbox_yellow,
    alertbox_purple, alertbox_orange, alertbox_pink, alertbox_cyan,
    alertbox_lime, alertbox_brown, alertbox_gray, alertbox_black,

    # Toasts
    toast, toast_red, toast_green, toast_blue,
    toast_black, toast_pink,

    # Math
    add, subtract, multiply, divide, modulus, exponent, power,
    square, cube, squareroot, cuberoot, absolutevalue, floordivision, roundoff,

    # Trigonometry and Logs
    sine, cosine, tangent, arctangent,
    log_base_2, log_base_10, natural_log,

    # Random
    randint, randfloat,
    randomintpositive, randomintnegative,
    randomfloatpositive, randomfloatnegative,

    # Constants
    pi, e, goldenratio, tau,
    speedoflight, planckconstant, gravitationalconstant,
    electronmass, protonmass, neutronmass,
    electronvolt, joule, kilojoule, megajoule,
    gigajoule, terajoule, petajoule, exajoule,
)

__all__ = [
    # Web
    "htmlcssjs", "image",

    # Core UI
    "write", "title", "header", "subheader", "caption",

    # Alert Boxes
    "alertbox_red", "alertbox_green", "alertbox_blue", "alertbox_yellow",
    "alertbox_purple", "alertbox_orange", "alertbox_pink", "alertbox_cyan",
    "alertbox_lime", "alertbox_brown", "alertbox_gray", "alertbox_black",

    # Toasts
    "toast", "toast_red", "toast_green", "toast_blue",
    "toast_black", "toast_pink",

    # Math
    "add", "subtract", "multiply", "divide", "modulus", "exponent", "power",
    "square", "cube", "squareroot", "cuberoot", "absolutevalue", "floordivision", "roundoff",

    # Trigonometry and Logs
    "sine", "cosine", "tangent", "arctangent",
    "log_base_2", "log_base_10", "natural_log",

    # Random
    "randint", "randfloat",
    "randomintpositive", "randomintnegative",
    "randomfloatpositive", "randomfloatnegative",

    # Constants
    "pi", "e", "goldenratio", "tau",
    "speedoflight", "planckconstant", "gravitationalconstant",
    "electronmass", "protonmass", "neutronmass",
    "electronvolt", "joule", "kilojoule", "megajoule",
    "gigajoule", "terajoule", "petajoule", "exajoule"
]

__version__ = "0.1.9"
__author__ = "Ibrahim Akhlaq"
__email__ = "ibakhlaq@gmail.com"
__license__ = "MIT"
__description__ = "A powerful Python toolkit with automatic HTML output and utilities by Ibrahim Akhlaq"

__classifiers__ = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]