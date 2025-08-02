import html as html_escape
import webbrowser
import tempfile
import random
import atexit
import uuid
import math
import os
import sys
import urllib.parse

_output_buffer = []
_output_file_path = None

def write(*args, sep=" ", end="\n"):
    joined = sep.join(str(arg) for arg in args) + end
    _output_buffer.append(joined + "<br>")

def image(src, width=None, height=None, alt=""):
    style = ""
    if width:
        style += f"width:{width}px;"
    if height:
        style += f"height:{height}px;"
    img_tag = f"<img src='{src}' alt='{html_escape.escape(alt)}' style='border-radius:7px;box-shadow: 0 4px 8px rgba(0,0,0,0.2), 0 6px 20px rgba(0,0,0,0.19);{style}'>"
    write(img_tag)

def htmlcssjs(html_fragment):
    cleaned = html_fragment.strip()
    cleaned = cleaned.replace("<html>", "").replace("</html>", "")
    cleaned = cleaned.replace("<body>", "").replace("</body>", "")
    cleaned = cleaned.replace("<head>", "").replace("</head>", "")
    cleaned = cleaned.replace("<!DOCTYPE html>", "")
    write(cleaned)

def _auto_render():
    global _output_file_path
    if not _output_buffer:
        return

    html_content = "\n".join(_output_buffer)
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title></title>
        <style>
            body {{
                font-family: sans-serif;
                padding: 20px;
                line-height: 1.6;
            }}
            #output {{
                white-space: normal;
            }}
        </style>
    </head>
    <body>
        <div id="output">{html_content}</div>
    </body>
    </html>
    """

    # Use a stable file path
    temp_path = os.path.join(tempfile.gettempdir(), "pytpro_output.html")
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(html_template)

    _output_file_path = temp_path
    webbrowser.open(f"file://{_output_file_path}")
    _output_buffer.clear()

atexit.register(_auto_render)

# -----------------------------
# Math and utility functions
# -----------------------------

def add(a, b):
    """find the sum of two numbers. in other words, add 2 numbers together."""
    result = a + b
    write(result)
    return result

def subtract(a, b):
    """find the difference of two numbers. in other words, subtract the second number from the first."""
    result = a - b
    write(result)
    return result

def multiply(a, b):
    """find the product of two numbers. in other words, find the result of a multiplication."""
    result = a * b
    write(result)
    return result

def divide(a, b):
    """find the division of two numbers. in other words, find the result of a fraction."""
    result = a / b
    write(result)
    return result

def modulus(a, b):
    """find the remainder of two numbers in a fraction. Inputs must be integers."""
    result = a % b
    write(result)
    return result

def exponent(a, b):
    """find the exponent/power of two numbers. The first number is the base and the second is the power."""
    result = a ** b
    write(result)
    return result

def power(a, b):
    """find the exponent/power of two numbers. The first number is the base and the second is the power."""
    result = math.pow(a, b)
    write(result)
    return result

def floordivision(a, b):
    """find the floor division of two numbers."""
    result = a // b
    write(result)
    return result

def squareroot(a):
    """find the square root of a number."""
    result = math.sqrt(a)
    write(result)
    return result

def cuberoot(a):
    """find the cube root of a number."""
    result = a ** (1 / 3)
    write(result)
    return result

def square(a):
    """find the square of a number."""
    result = a ** 2
    write(result)
    return result

def cube(a):
    """find the cube of a number."""
    result = a ** 3
    write(result)
    return result

def absolutevalue(a):
    """find the absolute value of a number."""
    result = abs(a)
    write(result)
    return result

def roundoff(a):
    """round a number to the nearest integer."""
    result = round(a)
    write(result)
    return result

# -----------------------------
# Random number functions
# -----------------------------

def randomfloatpositive(start, end):
    """Returns a positive random float between start and end."""
    result = abs(random.uniform(start, end))
    write(result)
    return result

def randomintpositive(start, end, step=1):
    """Returns a positive random integer from start to end with step."""
    result = abs(random.randrange(start, end + 1, step))
    write(result)
    return result

def randint(start=0, end=100):
    """Returns a random integer between start and end."""
    result = random.randint(start, end)
    write(result)
    return result

def randfloat():
    """Returns a random float between 0 and 1."""
    result = random.random()
    write(result)
    return result

def randomfloatnegative(start, end):
    """Returns a negative random float between start and end."""
    result = -abs(random.uniform(start, end))
    write(result)
    return result

def randomintnegative(start, end, step=1):
    """Returns a negative random integer from start to end with step."""
    result = -abs(random.randrange(start, end + 1, step))
    write(result)
    return result

# -----------------------------
# Trigonometry and log functions
# -----------------------------

def sine(x):
    """Return the sine of x (in radians)."""
    result = math.sin(x)
    write(result)
    return result

def cosine(x):
    """Return the cosine of x (in radians)."""
    result = math.cos(x)
    write(result)
    return result

def tangent(x):
    """Return the tangent of x (in radians)."""
    result = math.tan(x)
    write(result)
    return result

def arctangent(x):
    """Return the arctangent of x (in radians)."""
    result = math.atan(x)
    write(result)
    return result

def log_base_10(x):
    """Return the log base 10 of x."""
    result = math.log10(x)
    write(result)
    return result

def log_base_2(x):
    """Return the log base 2 of x."""
    result = math.log2(x)
    write(result)
    return result

def natural_log(x):
    """Return the natural log (base e) of x."""
    result = math.log(x)
    write(result)
    return result

# -----------------------------
# Mathematical Constants
# -----------------------------

class AutoWriteFloat:
    def __init__(self, value, description=""):
        self.value = value
        self.description = description

    def __str__(self):
        write(self.value)
        return str(self.value)

    def __repr__(self):
        return str(self.value)
    
pi = AutoWriteFloat(math.pi, "Return the value of π (pi).")

e = AutoWriteFloat(math.e, "Return the value of e (Euler’s number).")

goldenratio = AutoWriteFloat((1 + math.sqrt(5)) / 2, "Return φ (the golden ratio).")

tau = AutoWriteFloat(math.tau, "Return τ (the tau constant).")

# -----------------------------
# Scientific Constants
# -----------------------------

speedoflight = AutoWriteFloat(299792458, "Return the speed of light (c) in m/s.")

planckconstant = AutoWriteFloat(6.62607004e-34, "Return the Planck constant (h) in J⋅s.")

gravitationalconstant = AutoWriteFloat(6.67408e-11, "Return the gravitational constant (G) in m3⋅kg−1⋅s−2.")

electronmass = AutoWriteFloat(9.10938356e-31, "Return the mass of an electron (me) in kg.")

protonmass = AutoWriteFloat(1.6726219e-27, "Return the mass of a proton (mp) in kg.")

neutronmass = AutoWriteFloat(1.674927471e-27, "Return the mass of a neutron (mn) in kg.")

electronvolt = AutoWriteFloat(1.602176634e-19, "Return the electron volt (eV) in J.")

joule = AutoWriteFloat(1, "Return the joule (J) in J.")

kilojoule = AutoWriteFloat(1000, "Return the kilojoule (kJ) in J.")

megajoule = AutoWriteFloat(1000000, "Return the megajoule (MJ) in J.")

gigajoule = AutoWriteFloat(1000000000, "Return the gigajoule (GJ) in J.")

terajoule = AutoWriteFloat(1000000000000, "Return the terajoule (TJ) in J.")

petajoule = AutoWriteFloat(1000000000000000, "Return the petajoule (PJ) in J.")

exajoule = AutoWriteFloat(1000000000000000000, "Return the exajoule (EJ) in J.")

# ------------------------------
# streamlit-like functions, etc.
# ------------------------------

def header(text):
    """Display a secondary header."""
    write(f"<h2>{html_escape.escape(str(text))}</h2>")

def subheader(text):
    """Display a smaller subheader."""
    write(f"<h3>{html_escape.escape(str(text))}</h3>")

def caption(text):
    """Display a small caption or note."""
    write(f"<p style='font-size: 0.9em; color: gray;'>{html_escape.escape(str(text))}</p>")

def title(text):
    """Display a title in large bold text."""
    write(f"<h1>{html_escape.escape(str(text))}</h1>")

def alertbox_red(text):
    """Display a red alert box."""
    safe_text = html_escape.escape(str(text))
    html = f"""
    <div style='
        padding: 16px;
        margin: 10px 0;
        background-color: #fdecea;
        color: #b00020;
        border-left: 6px solid #b00020;
        border-radius: 4px;
        font-family: sans-serif;
    '>
        {safe_text}
    </div>
    """
    write(html)

def alertbox_green(text):
    """Display a green alert box."""
    safe_text = html_escape.escape(str(text))
    html = f"""
    <div style='
        padding: 16px;
        margin: 10px 0;
        background-color: #e8f5e9;
        color: #2e7d32;
        border-left: 6px solid #2e7d32;
        border-radius: 4px;
        font-family: sans-serif;
    '>
        {safe_text}
    </div>
    """
    write(html)

def alertbox_blue(text):
    """Display a blue alert box."""
    safe_text = html_escape.escape(str(text))
    html = f"""
    <div style='
        padding: 16px;
        margin: 10px 0;
        background-color: #e3f2fd;
        color: #1976d2;
        border-left: 6px solid #1976d2;
        border-radius: 4px;
        font-family: sans-serif;
    '>
        {safe_text}
    </div>
    """
    write(html)

def alertbox_yellow(text):
    """Display a yellow alert box."""
    safe_text = html_escape.escape(str(text))
    html = f"""
    <div style='
        padding: 16px;
        margin: 10px 0;
        background-color: #fffde7;
        color: #fbc02d;
        border-left: 6px solid #fbc02d;
        border-radius: 4px;
        font-family: sans-serif;
    '>
        {safe_text}
    </div>
    """
    write(html)

def alertbox_purple(text):
    """Display a purple alert box."""
    safe_text = html_escape.escape(str(text))
    html = f"""
    <div style='
        padding: 16px;
        margin: 10px 0;
        background-color: #f3e5f5;
        color: #8e24aa;
        border-left: 6px solid #8e24aa;
        border-radius: 4px;
        font-family: sans-serif;
    '>
        {safe_text}
    </div>
    """
    write(html)

def alertbox_orange(text):
    """Display an orange alert box."""
    safe_text = html_escape.escape(str(text))
    html = f"""
    <div style='
        padding: 16px;
        margin: 10px 0;
        background-color: #fff3e0;
        color: #f57c00;
        border-left: 6px solid #f57c00;
        border-radius: 4px;
        font-family: sans-serif;
    '>
        {safe_text}
    </div>
    """
    write(html)

def alertbox_pink(text):
    """Display a pink alert box."""
    safe_text = html_escape.escape(str(text))
    html = f"""
    <div style='
        padding: 16px;
        margin: 10px 0;
        background-color: #fce4ec;
        color: #c2185b;
        border-left: 6px solid #c2185b;
        border-radius: 4px;
        font-family: sans-serif;
    '>
        {safe_text}
    </div>
    """
    write(html)

def alertbox_cyan(text):
    """Display a cyan alert box."""
    safe_text = html_escape.escape(str(text))
    html = f"""
    <div style='
        padding: 16px;
        margin: 10px 0;
        background-color: #e0f7fa;
        color: #00acc1;
        border-left: 6px solid #00acc1;
        border-radius: 4px;
        font-family: sans-serif;
    '>
        {safe_text}
    </div>
    """
    write(html)

def alertbox_lime(text):
    """Display a lime alert box."""
    safe_text = html_escape.escape(str(text))
    html = f"""
    <div style='
        padding: 16px;
        margin: 10px 0;
        background-color: #f1f8e9;
        color: #c0ca33;
        border-left: 6px solid #c0ca33;
        border-radius: 4px;
        font-family: sans-serif;
    '>
        {safe_text}
    </div>
    """
    write(html)

def alertbox_brown(text):
    """Display a brown alert box."""
    safe_text = html_escape.escape(str(text))
    html = f"""
    <div style='
        padding: 16px;
        margin: 10px 0;
        background-color: #efebe9;
        color: #795548;
        border-left: 6px solid #795548;
        border-radius: 4px;
        font-family: sans-serif;
    '>
        {safe_text}
    </div>
    """
    write(html)

def alertbox_gray(text):
    """Display a gray alert box."""
    safe_text = html_escape.escape(str(text))
    html = f"""
    <div style='
        padding: 16px;
        margin: 10px 0;
        background-color: #f5f5f5;
        color: #616161;
        border-left: 6px solid #616161;
        border-radius: 4px;
        font-family: sans-serif;
    '>
        {safe_text}
    </div>
    """
    write(html)

def alertbox_black(text):
    """Display a black alert box."""
    safe_text = html_escape.escape(str(text))
    html = f"""
    <div style='
        padding: 16px;
        margin: 10px 0;
        background-color: #eeeeee;
        color: #212121;
        border-left: 6px solid #212121;
        border-radius: 4px;
        font-family: sans-serif;
    '>
        {safe_text}
    </div>
    """
    write(html)

def toast_red(text):
    """Display a red toast message (disappears after 1.5 seconds)."""
    safe_text = html_escape.escape(str(text))
    html = f"""
    <div style='
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background-color: #fdecea;
        color: #b00020;
        padding: 12px 20px;
        border-radius: 6px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        font-family: sans-serif;
        z-index: 9999;
        animation: fadeout 1.5s forwards;
    '>
        {safe_text}
    </div>
    <style>
    @keyframes fadeout {{
        0% {{ opacity: 1; }}
        70% {{ opacity: 1; }}
        100% {{ opacity: 0; display: none; }}
    }}
    </style>
    """
    write(html)

def toast_green(text):
    """Display a green toast message (disappears after 1.5 seconds)."""
    safe_text = html_escape.escape(str(text))
    html = f"""
    <div style='
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 12px 20px;
        border-radius: 6px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        font-family: sans-serif;
        z-index: 9999;
        animation: fadeout 1.5s forwards;
    '>
        {safe_text}
    </div>
    <style>
    @keyframes fadeout {{
        0% {{ opacity: 1; }}
        70% {{ opacity: 1; }}
        100% {{ opacity: 0; display: none; }}
    }}
    </style>
    """
    write(html)

def toast_blue(text):
    """Display a blue toast message (disappears after 1.5 seconds)."""
    safe_text = html_escape.escape(str(text))
    html = f"""
    <div style='
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 12px 20px;
        border-radius: 6px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        font-family: sans-serif;
        z-index: 9999;
        animation: fadeout 1.5s forwards;
    '>
        {safe_text}
    </div>
    <style>
    @keyframes fadeout {{
        0% {{ opacity: 1; }}
        70% {{ opacity: 1; }}
        100% {{ opacity: 0; display: none; }}
    }}
    </style>
    """
    write(html)

def toast_black(text):
    """Display a black toast message (disappears after 1.5 seconds)."""
    safe_text = html_escape.escape(str(text))
    html = f"""
    <div style='
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background-color: #eeeeee;
        color: #212121;
        padding: 12px 20px;
        border-radius: 6px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        font-family: sans-serif;
        z-index: 9999;
        animation: fadeout 1.5s forwards;
    '>
        {safe_text}
    </div>
    <style>
    @keyframes fadeout {{
        0% {{ opacity: 1; }}
        70% {{ opacity: 1; }}
        100% {{ opacity: 0; display: none; }}
    }}
    </style>
    """
    write(html)

def toast_pink(text):
    """Display a pink toast message (disappears after 1.5 seconds)."""
    safe_text = html_escape.escape(str(text))
    html = f"""
    <div style='
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background-color: #fce4ec;
        color: #c2185b;
        padding: 12px 20px;
        border-radius: 6px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        font-family: sans-serif;
        z-index: 9999;
        animation: fadeout 1.5s forwards;
    '>
        {safe_text}
    </div>
    <style>
    @keyframes fadeout {{
        0% {{ opacity: 1; }}
        70% {{ opacity: 1; }}
        100% {{ opacity: 0; display: none; }}
    }}
    </style>
    """
    write(html)

def toast(text):
    """Display a default toast message (disappears after 1.5 seconds)."""
    safe_text = html_escape.escape(str(text))
    html = f"""
    <div style='
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background-color: #ffffff;
        color: #212121;
        padding: 12px 20px;
        border-radius: 6px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        font-family: sans-serif;
        z-index: 9999;
        animation: fadeout 1.5s forwards;
    '>
        {safe_text}
    </div>
    <style>
    @keyframes fadeout {{
        0% {{ opacity: 1; }}
        70% {{ opacity: 1; }}
        100% {{ opacity: 0; display: none; }}
    }}
    </style>
    """
    write(html)