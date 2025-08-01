# kzstack

`kzstack` is a package to stack images for many purposes.

There are many use cases, but it is especially important in long-exposure photography and astrophotography.

- HomePage: https://github.com/kzhu2099/KZ-Stack
- Issues: https://github.com/kzhu2099/KZ-Stack/issues

[![PyPI Downloads](https://static.pepy.tech/badge/kzstack)](https://pepy.tech/projects/kzstack) ![PyPI version](https://img.shields.io/pypi/v/kzstack.svg)

Author: Kevin Zhu

## Features

- ability to stack images
- gamma correction accounted for
- custom quality / denoising functions
- image showing / saving
- bias usage

## Installation

To install `kzstack`, use pip: ```pip install kzstack```.

However, many prefer to use a virtual environment.

macOS / Linux:

```sh
# make your desired directory
mkdir /path/to/your/directory
cd /path/to/your/directory

# setup the .venv (or whatever you want to name it)
pip install virtualenv
python3 -m venv .venv

# install kzstack
source .venv/bin/activate
pip install kzstack

deactivate # when you are completely done
```

Windows CMD:

```sh
# make your desired directory
mkdir C:path\to\your\directory
cd C:path\to\your\directory

# setup the .venv (or whatever you want to name it)
pip install virtualenv
python3 -m venv .venv

# install kzstack
.venv\Scripts\activate
pip install kzstack

deactivate # when you are completely done
```

## Usage

**PLEASE HAVE ALIGNED IMAGES!! STACKING WILL NOT TURN OUT GOOD OTHERWISE**

First, import KZStack and all its functions (for denoising / quality).

Follow the provided `stack_accumualte.ipynb` for your data (change the path).

After, you may choose to use the average or input your own denoising / quality control functions.

These must be in the format of `def func(image)`, without additional parameters. Other `parameters` (like a threshold) should not be `args` to the function.

## License

The License is an MIT License found in the LICENSE file.