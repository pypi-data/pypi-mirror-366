# Ansy

[![GitHub Repository](https://img.shields.io/badge/-GitHub-%230D0D0D?logo=github&labelColor=gray)](https://github.com/anas-shakeel/ansy)
[![Latest PyPi version](https://img.shields.io/pypi/v/ansy.svg)](https://pypi.python.org/pypi/ansy)
[![supported Python versions](https://img.shields.io/pypi/pyversions/ansy)](https://pypi.python.org/pypi/ansy)
[![Project licence](https://img.shields.io/pypi/l/ansy?color=blue)](LICENSE)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](black)
[![Automated testing results](https://img.shields.io/github/actions/workflow/status/anas-shakeel/ansy/.github/workflows/test.yml?branch=main)](https://github.com/anas-shakeel/ansy/actions/workflows/test.yml?query=branch%3Amain)
[![PyPI downloads](https://static.pepy.tech/badge/ansy)](https://pypi.org/project/ansy/)

`ansy` (_pronounced ANSI_), inspired by `termcolor`, is a _lightweight python library_ used to style and format output in the terminal.

## ✨ Features

-   Easy text coloring and styling using intuitive functions
-   Support for **4-bit**, **8-bit**, and **24-bit** (truecolor) color modes
-   **Gradients**, **palettes**, and **random color** generation
-   Cross-platform support _(Windows, Linux, macOS)_

### 📦 Installation

Ansy is available on **PyPI** and can be installed with `pip`.

```shell
pip install ansy
```

or Install from source:

```shell
git clone https://github.com/anas-shakeel/ansy.git
cd ansy
pip install .
```

You may also need to install `colorama` (_**Windows** users only_).

### 🚀 Quick Usage

```python
from ansy import colored

print(colored("Hello, World!", fgcolor="cyan", bgcolor="black", attrs=["bold"]))
```

OR 

```python
from ansy import colored_gradient

print(colored_gradient(text, "#00ffff", "#b00b1e"))
```

### 📚 Documentation

Full documentation is available [here](https://anas-shakeel.github.io/ansy/)

### 🤝 Contributing

Contributions are welcome! Check out the [contributing guide](https://anas-shakeel.github.io/ansy/contributing/) to get started.

### 💻 Compatibility

This package has been well-tested across three major platforms (**Windows**, **MacOS**, and **Linux/ubuntu**).

It supports Python versions `3.8` upto `3.13`. it may or may not work on other versions. [See more](https://anas-shakeel.github.io/ansy/compatibility/)

## Preview

![A preview of Ansy in action](https://raw.githubusercontent.com/Anas-Shakeel/ansy/refs/heads/main/docs/images/demo.gif)

Made with ❤️ to make your terminal output more beautiful.
