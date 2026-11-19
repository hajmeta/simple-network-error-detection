# Network Error Detection

A small educational Python program that simulates **error detection and correction codes** used in computer networks. It acts as both a **sender** (calculates the extra bits) and a **receiver** (checks the received data), so you can type in a corrupted message and see whether the method catches the error.

No external libraries are needed, only Python 3.8+.

## Supported methods

| Method | Command | Detects | Corrects |
|---|---|---|---|
| Simple parity bit (even) | `parity` | odd number of bit errors | no |
| 2D parity | `2d` | 1, 2 or 3 bit errors | single-bit errors |
| Checksum (one's complement) | `checksum` | most errors, but not swapped words | no |
| CRC (XOR division) | `crc` | single, double and burst errors (depends on generator) | no |
| Hamming code | `hamming` | up to 2 bit errors | single-bit errors |

## How to run

```
python error_codes_network.py
```

The program asks for:

1. The method (`parity`, `2d`, `checksum`, `crc` or `hamming`)
2. The number of codes and the length of each code (shorter codes are padded with zeros)
3. The codes of the sender
4. The **received data** (what arrives after noise, so change some bits on purpose)

The receiver only types the data bits. The check bits (parity bits, checksum, CRC, Hamming check bits) are taken from the sender and attached automatically. Input is validated (only `0` and `1`, correct lengths).

## Examples

### 2D parity: single-bit error is found and corrected

Sender codes: `1001`, `1101`, `1111`. Received: `1000`, `1101`, `1111`.

```
Sender table:
1 0 0 1 | 0
1 1 0 1 | 1
1 1 1 1 | 0
-----------
1 0 1 1 | 1

Results:
Row 1: parity does not match -> wrong
Column 4: parity does not match -> wrong

Single-bit error detected at row 1, column 4.
```

### CRC: single-bit error is detected

Data `1101011011`, generator `10011`, received `1101011010`.

```
Data: 1101011011, CRC: 1110 ==> Frame: 11010110111110
Code 1: frame = 11010110101110, remainder = 0011
Code 1: error detected! (remainder is not zero)
```

### Hamming (7,4)

Data `1011` becomes `0110011`. If the received data is `1001`, the program finds the error at position 6 and corrects it.

### Errors that are *not* detected

The program also shows the weak points of each method:

- **Parity:** flipping two bits keeps the parity the same.
- **2D parity:** flipping four bits at the corners of a rectangle is not detected.
- **Checksum:** swapping the order of two words gives the same sum.
- **CRC:** an error pattern equal to the generator itself is not detected.
- **Hamming:** two-bit errors are "corrected" to the wrong data (the program warns about this).

## Tests

The calculation functions are separated from the input/output code, so they can be tested automatically:

```
python -m unittest -v
```

## Project structure

```
error_codes_network.py   main program (calculations, input functions, one run_ function per method)
test_error_codes.py      unit tests
```

## Notes

Developed as a study project for computer networks.
