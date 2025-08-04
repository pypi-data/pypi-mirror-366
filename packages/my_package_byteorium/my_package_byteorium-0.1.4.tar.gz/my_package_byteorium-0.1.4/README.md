# Python project template byteorium

[![Create Release](https://github.com/mab0189/python_project_template/actions/workflows/release.yml/badge.svg)](https://github.com/mab0189/python_project_template/actions/workflows/release.yml)

Python project template for building robust, modern, and clean Python projects according to my personal preferences. 
Includes thorough code quality checks and developer-friendly tools.

---

## Table of contents

- [Features](#features)
- [Requirements](#requirements)
- [Setup](#setup)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Dependency management**: Easy dependency management with `poetry`.
- **Code quality tools**: 
  - `ruff` for formatting, linting and coding standards.
  - `pytest` for testing.
  - `mypy` for typechecking.
- **Documentation**: Sphinx setup with RTD theme and `myst-parser` for Markdown support.
- **Easy usage**: Pre-configured `tox` workflow for a streamlined development experience.
- **Best Practices**: Adherence to PEP 8 and other modern Python standards.

---

## Requirements

Ensure you have the following installed:

- Python 3.12
- [Poetry](https://python-poetry.org/) is required for the dependency management

---

## Setup

Follow these steps to set up the project environment:

1. Clone the repository:
   ```bash
   git clone https://github.com/mab0189/python_project_template_byteorium.git
   cd python_project_template_byteorium
   ```
   
2. Set up a virtual environment with  `poetry` with all dependencies:
   ```bash
   poetry install
   ```

---

## Usage

[Tox](https://tox.readthedocs.io/) is used to manage and automate testing, linting, formatting, and more. 
Below are the available environments configured in the `tox.ini`:

| Environment     | Description                                               | Command to Run         |
|-----------------|-----------------------------------------------------------|------------------------|
| `py312`         | Test code on Python 3.12                                  | `tox -e py312`         |
| `isort`         | Check and sort imports                                    | `tox -e isort`         |
| `format`        | Auto-format code with `ruff`                              | `tox -e format`        |     
| `lint`          | Lint code with `ruff`                                     | `tox -e lint`          |
| `typecheck`     | Perform static type checking with `mypy`                  | `tox -e typecheck`     |
| `test`          | Run tests with `pytest` and `poetry` managed dependencies | `tox -e test`          |
| `docs`          | Build Sphinx HTML documentation                           | `tox -e docs`          |

---

## Contributing

Contributions are welcome but this project is developed according to my personal preferences.

---

## License

This project is licensed under the [MIT License](LICENSE).
