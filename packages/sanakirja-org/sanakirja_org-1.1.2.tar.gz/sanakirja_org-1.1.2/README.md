# sanakirja-org

[![License](https://img.shields.io/github/license/AceHanded/sanakirja-org?style=for-the-badge)](https://github.com/AceHanded/sanakirja-org/blob/main/LICENSE)[![CC BY-SA 3.0](https://img.shields.io/badge/CC--BY--SA--3.0-orange?style=for-the-badge)](https://github.com/AceHanded/sanakirja-org/blob/main/LICENSE.CC-BY-SA)
[![GitHubStars](https://img.shields.io/github/stars/AceHanded/sanakirja-org?style=for-the-badge&logo=github&labelColor=black)](https://github.com/AceHanded/sanakirja-org)
[![PyPI](https://img.shields.io/pypi/dd/sanakirja-org?style=for-the-badge&logo=pypi&logoColor=white&labelColor=blue)](https://pypi.org/project/sanakirja-org/)
[![BuyMeACoffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/acehand)

An unofficial Python API and CLI tool for sanakirja.org.

## Installation

```bash
pip install sanakirja-org
```

## Examples

### Language codes

```python
import sanakirja as sk

sanakirja = sk.Sanakirja()

# The below formats are all equivalent
sanakirja.search(q="life", l=sk.LangCodes.en)
sanakirja.search(q="life", l="en")
sanakirja.search(q="life", l=3)
```

### Basic search

```python
import sanakirja as sk

sanakirja = sk.Sanakirja()

# No language codes specified -> source language is guessed and simple translations are provided for each language
sanakirja.search(q="everything")

# No target language code specified -> simple translations are provided from the source language to each language
sanakirja.search(q="everything", l=sk.LangCodes.en)

# No source language code specified -> source language is guessed and accurate translations are provided for the target language
sanakirja.search(q="everything", l2=sk.LangCodes.fi)

# Both language codes specified -> accurate translations are provided from the source language to the target language
sanakirja.search(q="everything", l=sk.LangCodes.en, l2=sk.LangCodes.fi)
```

### Error handling

```python
import sanakirja as sk

sanakirja = sk.Sanakirja()

try:
    sk_res = sanakirja.search(q="universe", l=42)
except sk.LanguageCodeError as e:
    print(e)  # Invalid language code: '42'
```

> [!TIP]
> Valid language codes can be viewed, for example, via the `__members__` attribute of the `LangCodes` IntEnum.

### CLI

```bash
sanakirja --from fi --to 3 --lang sv --show="all,-translations" --pretty 2 --output "./result.json" kivi
```

The above example performs a search for the query "kivi" from Finnish to English. The language of user interface elements is set to Swedish, the "translations" field is omitted and the indent level is set to 2. Finally, the result is saved into a file named "result.json" at the current directory.

> [!NOTE]
> The argument `-h, --help` provides more information about each argument.

## Attribution and licensing

This package is licensed under the [MIT License](LICENSE).

It makes use of content retrieved from [sanakirja.org](https://sanakirja.org), a web service provided by Sanakirja.org Solutions Oy. The content is licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License ([CC BY-SA 3.0](LICENSE.CC-BY-SA)). \
This package is **not** affiliated with or endorsed by sanakirja.org.

If you redistribute content fetched using this package, you are responsible for complying with the terms of the CC BY-SA license, including proper attribution.