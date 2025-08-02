<p align="center">
  <img src="https://i.postimg.cc/BjSmyvYv/download.png" width="200" alt="pytpro logo">
</p>
---
# pytpro

**pytpro** is a lightweight Python package by Ibrahim Akhlaq that provides powerful utility functions for math, randomness, and HTML rendering. It's clean, minimal, and built to feel like magic.

---

## 🚀 Features

### ➕ Math Functions
- `add(a, b)` / `subtract(a, b)`
- `multiply(a, b)` / `divide(a, b)`
- `modulus(a, b)` / `floordivision(a, b)`
- `square(a)` / `cube(a)`
- `squareroot(a)` / `cuberoot(a)`
- `absolutevalue(a)` / `roundoff(a)`
- `exponent(a, b)` / `power(a, b)`

### 🔢 Random Number Generators
- `randint(start=0, end=100)`
- `randfloat()`
- `randomintpositive(start, end, step=1)`
- `randomintnegative(start, end, step=1)`
- `randomfloatpositive(start, end)`
- `randomfloatnegative(start, end)`

### 📐 Trigonometry & Logs
- `sine(x)` / `cosine(x)` / `tangent(x)` / `arctangent(x)`
- `log_base_2(x)` / `log_base_10(x)` / `natural_log(x)`

### 📏 Constants (Auto-displayed)
- `pi`, `e`, `goldenratio`, `tau`
- `speedoflight`, `planckconstant`, `gravitationalconstant`
- `electronmass`, `protonmass`, `neutronmass`
- `electronvolt`, `joule`, `kilojoule`, `megajoule`, `gigajoule`, `terajoule`, `petajoule`, `exajoule`

---

### Text
- `write(...)`
- `title(text)`
- `header(text)`
- `subheader(text)`
- `caption(text)`

### HTML Embeds
- `htmlcssjs(html_fragment)`

### Alert Boxes
- `alertbox_red(text)` / `alertbox_green(text)` / `alertbox_blue(text)`
- `alertbox_yellow(text)` / `alertbox_purple(text)` / `alertbox_orange(text)`
- `alertbox_pink(text)` / `alertbox_cyan(text)` / `alertbox_lime(text)`
- `alertbox_brown(text)` / `alertbox_gray(text)` / `alertbox_black(text)`

### Toast Notifications (auto-fade)
- `toast(text)` – white default
- `toast_red(text)` / `toast_green(text)` / `toast_blue(text)`
- `toast_black(text)` / `toast_pink(text)`

---

## 🖥️ Example Usage

```python
import pytpro

pytpro.add(2, 3)
pytpro.square(6)
pytpro.pi()
pytpro.htmlcssjs("<h1>Hello!</h1><p>This is raw HTML.</p>")
```

# 🖥️ Instructions to install:

To install locally from your project directory, open PowerShell or terminal and run:

```bash
pip install pytpro
```

__version:0.3.0__