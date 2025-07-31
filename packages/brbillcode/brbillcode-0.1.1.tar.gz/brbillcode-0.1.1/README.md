# Brbillcode

`brbillcode` is a Python library for extracting and validating data from Brazilian payment slips ("boletos") — including both bank boletos and collection boletos (such as utilities like electricity and water). It supports parsing from both barcode strings and digitable lines, providing detailed structured information and validation based on Brazilian standards.

## Features

- Parse bank boletos and collection boletos from:
  - Digitable lines (47 or 48 digits)
  - Barcodes (44 digits)
- Extract detailed information such as:
  - Bank/collection identifiers
  - Currency code
  - Expiration date calculation
  - Payment amount
  - Verification digits with modulus 10 and modulus 11 algorithms
- Validate boletos with correct check digit verification
- Convert collection boleto digitable lines to barcodes and vice versa
- Supports different modulus 11 variants used in bank and collection boletos

## Installation

```bash
pip install brbillcode
````

*(Note: adjust if publishing to PyPI or installing locally.)*

## Usage

```python
from brbillcode.core.line import Line

# Example digitable line for a bank boleto
line_code = "00190500954014481606906809350314337370000000100"

line = Line(line_code)

print("Barcode:", line.get_bar())
print("Digitable line (formatted):", line.get_line(formatted=True))
print("Is valid?", line.validate())
print("Extracted info:", line.get_code_info())
```

Supports both bank and collection boletos; the library automatically detects the boleto type based on input length and format.

## Supported Code Types

| Code Length | Type                   |
| ----------- | ---------------------- |
| 44 digits   | Barcode                |
| 47 digits   | Bank boleto line       |
| 48 digits   | Collection boleto line |

## Module Overview

* `core/line.py`: Main class `Line` to abstract boleto parsing and delegate to bank or collection boleto handlers.
* `models/bank.py`: Handles bank boleto parsing, info extraction, validation.
* `models/collection.py`: Handles collection boleto parsing, info extraction, validation.
* `utils/modules.py`: Implements modulo 10 and modulo 11 algorithms used for check digits.

## License

MIT License

---

## References

* Brazilian "boleto" specifications and standards.
* Modulus 10 and modulus 11 algorithms for check digits.