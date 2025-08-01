# xdep

[![PyPI version](https://img.shields.io/pypi/v/xdep.svg)](https://pypi.org/project/xdep/)
[![Python Version](https://img.shields.io/pypi/pyversions/xdep.svg)](https://pypi.org/project/xdep/)
[![License](https://img.shields.io/pypi/l/xdep.svg)](LICENSE)

---

## Screenshots

<img src="https://github.com/SAGAR-TAMANG/X-DEP/raw/master/static/ss-1.png" alt="screenshot of cmd terminal" />

| Accuracy & Loss Graphs | Explainability (LIME)  |
| :---------------: | :---------------: |
| <img src="https://github.com/SAGAR-TAMANG/X-DEP/raw/master/static/ss-3.png" alt="Accuracy & Loss Graphs" /> | <img src="https://github.com/SAGAR-TAMANG/X-DEP/raw/master/static/ss-2.png" alt="Explainability (LIME)" /> |

## Overview

**xdep** is an integrated pipeline designed to simplify the development and evaluation of trustworthy computer vision models.  
It provides an end-to-end framework for training, interpreting, and visualizing deep learning models with a focus on transparency and reliability.

---

## Features

- Easy setup and modular pipeline to build trustworthy computer vision models  
- Integrated support for popular explainability techniques (e.g., LIME)  
- Automated generation of evaluation reports and visualizations (CSV, figures)  
- Lightweight and easy to extend for custom workflows  
- Command-line interface (CLI) for quick experimentation and testing  

---

## Installation

You can install the latest stable version from [TestPyPI](https://test.pypi.org/project/xdep/) (for testing) or [PyPI](https://pypi.org/project/xdep/) (for production):

```bash
pip install xdep
```

---

## Dependencies

`xdep` requires the following Python packages (automatically installed with `pip`):

* `lime >= 0.2.0.1`
* `matplotlib`
* `pillow`
* `rich`
* `scikit-learn`
* `seaborn`
* `tensorflow`

---

## Quick Start

### Using as a Python Package

Here’s a minimal example of how to use `xdep` in your Python code:

```python
from xdep import main

# Call the main pipeline function or your preferred API
main.main()
```

---

### Using the CLI

After installation, you can run the `xdep` command directly in your terminal:

```bash
xdep
```

This will show available commands and options.

---

## Directory & Output Handling

`xdep` saves generated CSV files and figures to a `results` directory in the current working directory by default.

* If the `results` directory does not exist, it will be created automatically.
* You can configure output directories and filenames via the API or CLI arguments.

---

## Development & Contribution

Contributions are welcome! Feel free to:

* Report issues or bugs
* Request features or improvements
* Submit pull requests with enhancements or fixes

### Setup for Development

Clone the repo and install in editable mode:

```bash
git clone https://github.com/SAGAR-TAMANG/X-DEP
cd X-DEP
pip install -e .
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact

For questions, suggestions, or collaboration, reach out to:

**Sagar Tamang**
Email: [sagar.bdr0000@gmail.com](mailto:sagar.bdr0000@gmail.com)
GitHub: [https://github.com/SAGAR-TAMANG](https://github.com/SAGAR-TAMANG)

---

## Acknowledgements

* Thanks to the developers of [LIME](https://github.com/marcotcr/lime) and other open-source libraries integrated with this package.
* Inspired by the need for trustworthy and interpretable AI models in computer vision.

---

*Happy modeling!* 🚀
