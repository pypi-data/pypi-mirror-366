# lillib

A small collection of utility functions for Python.

## Installation

You can install the package via pip:

```bash
pip install lillib
```

## Usage

### Human-readable byte sizes

Convert byte sizes into human-readable strings:

```python
from lillib import humanbytes

# Basic usage (uses binary 1024-based units with IEC prefixes by default)
print(humanbytes(1024))  # "1.00 KiB"
print(humanbytes(1500000))  # "1.43 MiB"

# Using decimal (1000-based) units
print(humanbytes(1000, decimal=True))  # "1.00 KB"

# Control decimal places
print(humanbytes(1024, sigfig=0))  # "1 KiB"
print(humanbytes(1024, sigfig=3))  # "1.000 KiB"

# Control IEC strictness for binary units
print(humanbytes(1024, strict_iec=False))  # "1.00 KB" (non-strict)
```

## Features

- `humanbytes()`: Convert byte sizes into human-readable strings with appropriate unit prefixes
  - Support for both decimal (1000-based) and binary (1024-based) units
  - Support for IEC standard binary prefixes (KiB, MiB, GiB) or traditional prefixes

## License

This project is licensed under the GNU Affero General Public License v3 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
