# Standard Compression Scheme for Unicode

This package implements [SCSU](https://www.unicode.org/reports/tr6/tr6-4.html) as a Python text codec.

## Benefits of Unicode compression

Compressed strings typically have fewer bytes than strings encoded as [UTF-8](https://en.wikipedia.org/wiki/UTF-8) or [UTF-16](https://en.wikipedia.org/wiki/UTF-16).

| Sample Text                        | In UTF-8 | In UTF-16 | In SCSU  |
|------------------------------------|----------|-----------|----------|
| `¿Qué es Unicode?`                 | 18 bytes | 32 bytes  | 16 bytes |
| `Що таке Юнікод?`                  | 27 bytes | 30 bytes  | 16 bytes |
| `Ի՞նչ է Յունիկոդը ?`               | 32 bytes | 36 bytes  | 20 bytes |
| `यूनिकोड क्या है?`                 | 42 bytes | 32 bytes  | 17 bytes |
| `ユニコードとは何か？`                       | 30 bytes | 20 bytes  | 15 bytes |
| `什麼是Unicode(統一碼/標準萬國碼)?`           | 44 bytes | 44 bytes  | 38 bytes |
| `𐑢𐑳𐑑 𐑦𐑟 𐑿𐑯𐑦𐑒𐑴𐑛?`        | 47 bytes | 50 bytes  | 17 bytes |
| `😀😁😂😃😄😅😆😇😈😉😊😋😌😍😎😏` | 64 bytes | 64 bytes  | 19 bytes |

## Requirements

This package requires [Python 3.10](https://docs.python.org/3/whatsnew/3.10.html) or above.

## Usage

### Source code

Simply import the module and the SCSU codec is ready to use:

```python
import scsu

b = s.encode("SCSU")
```

To automatically add and remove a byte-order mark signature, use `SCSU-SIG` instead of `SCSU`.

### Command line interface

To compress a file, use the "encode" command: `python3 -m scsu encode unicode.txt > scsu.txt`

To decompress a file, use the "decode" command: `python3 -m scsu decode scsu.txt > unicode.txt`

To automatically add and remove a byte-order mark signature, add the `-s` option after the `encode`/`decode` command.

## Errata

[CPython bug #79792](https://github.com/python/cpython/issues/79792) causes the sample code (below) to not flush the encoding buffer:

```python
with open(file, mode="w", encoding="SCSU-SIG") as f:
    f.write(s)  # Never flushes the encoding buffer.
```

A workaround is to import the `codecs` module, then replace `open` with `codecs.open`:

```python
import codecs

with codecs.open(file, "w", encoding="SCSU-SIG") as f:
    f.write(s)  # Always flushes the encoding buffer.
```

## Credits

Encoding logic is heavily based on a sample encoder described in "[A survey of Unicode compression](https://www.unicode.org/notes/tn14/UnicodeCompression.pdf)" by Doug Ewell and originally written by Richard Gillam in his book _[Unicode Demystified](https://www.oreilly.com/library/view/unicode-demystified/0201700522/)_.

Enhancements to the encoding logic include:
* **A two-character lookahead buffer** to avoid a case where switching from Unicode to single-byte mode requires two window switches.
* **Compression of sequential static window characters** into a single new dynamic window, to avoid a case where a long string of punctuation is encoded as multiple quoted characters. 
* **Uses the [Latin-1 Supplement](https://www.unicode.org/charts/PDF/U0080.pdf) window whenever possible** so transcoding text encoded as ISO-8859-1 results in a valid SCSU _and_ ISO-8859-1 byte string.

Decoding logic, however, is entirely original.
