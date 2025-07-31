# mpy-file-info

A Python package and command-line tool for working with MicroPython `.mpy` files, providing a convenient wrapper around `mpy-tool`. This tool is compatible with [astral-sh/uv](https://github.com/astral-sh/uv) and can be run using `uvx mpy-file-info`.

## Features

- Hexdump and disassemble `.mpy` files
- Freeze `.mpy` files for embedding in firmware
- Merge multiple `.mpy` files
- Compatible with Python 3.13+
- Easily installable and runnable with [uv](https://github.com/astral-sh/uv)

## Installation

You can install this package locally, in a virtual environment, or directly with the `uvx` tool. If you are using [uv](https://github.com/astral-sh/uv):

```sh
uvx mpy-file-info --help
```