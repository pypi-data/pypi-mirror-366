import os
import json
import argparse
import sanakirja
from pathlib import Path
from typing import Set, Union

# All possible fields returned by the `search` method of the `Sanakirja` object
AVAILABLE_FIELDS = {
    "id", "url", "source_language", "target_language", "word", "transliteration", "gender", "additional_source_languages",
    "relations", "did_you_mean", "suggestions", "found_examples", "alternative_spellings", "multiple_spellings", 
    "synonyms", "pronunciations", "abbreviations", "inflections", "definitions", "examples", "categories", "translations"
}

def _parse_lang(lang: str) -> Union[int, str]:
    """
    Parse the given language code into proper `int` or `str` format.

    :param lang: The language code to parse.
    :type lang: str
    :return: The parsed language code in `int` or `str` format.
    :rtype: int | str
    """
    if lang.isdigit(): return int(lang)
    return lang.lower()

def _resolve_show_fields(show_arg: str) -> Set[str]:
    """
    Resolve the omitted fields from the `show` argument.

    :param show_arg: The contents of the `show` argument in `str` format.
    :type show_arg: str
    :return: The omitted fields as a set of strings.
    :rtype: set[str]
    """
    parts = {ppart for part in show_arg.split(",") if (ppart := part.strip().lower()) and ppart in AVAILABLE_FIELDS}

    omitted = set() if "all" in parts or all(part.startswith("-") for part in parts) else AVAILABLE_FIELDS.copy()
    if "all" in parts: parts.remove("all")

    for part in parts:
        key = part.lstrip("-")

        if part.startswith("-") and key not in omitted: omitted.add(key)
        elif not part.startswith("-") and key in omitted: omitted.remove(key)

    return omitted

def main() -> None:
    """The entry point of the unofficial CLI for the unofficial sanakirja.org API."""

    parser = argparse.ArgumentParser(description="Unofficial CLI for the unofficial sanakirja.org API")
    parser.add_argument("word", help="The word to search")
    parser.add_argument("--from", metavar="SRC", dest="source", type=_parse_lang, default=0, help="Source language (ISO code or integer e.g., 'fi' or 17) (default: 0)")
    parser.add_argument("--to", metavar="TGT", dest="target", type=_parse_lang, default=0, help="Target language (ISO code or integer, e.g., 'en' or 3) (default: 0)")
    parser.add_argument("-l", "--lang", "--language", metavar="LANG", type=_parse_lang, default="fi", help="The language of user interface elements (default: 'fi')")
    parser.add_argument("-s", "--show", metavar="FLDS", default="all", help="Fields to display, e.g., 'word,translations' or 'all,-similar_words' (default: 'all')")
    parser.add_argument("-p", "--pretty", metavar="INDT", nargs="?", type=int, const=4, help="Pretty-print the output with an optional indent level (default: 4)")
    parser.add_argument("-o", "--output", metavar="PATH", help="Save the result to a file at the specified path")
    parser.add_argument("-V", "--version", action="version", version=sanakirja.__version__)

    args = parser.parse_args()
    sk = sanakirja.Sanakirja()

    result = sk.search(q=args.word, l=args.source, l2=args.target, ui_lang=args.lang)
    omitted = _resolve_show_fields(args.show)
    output = {k: v for k, v in result.items() if k not in omitted}
    if not args.output: return print(json.dumps(output, indent=args.pretty, ensure_ascii=False))

    out_path = Path(args.output).expanduser()

    if out_path.exists() and out_path.is_dir():
        return print(f"\033[31mERROR\033[0m: The path '{out_path}' is a directory.")
    elif not out_path.parent.exists():
        return print(f"\033[31mERROR\033[0m: The directory '{out_path.parent}' does not exist.")
    elif not os.access(out_path.parent, os.W_OK):
        return print(f"\033[31mERROR\033[0m: Write access to '{out_path.parent}' denied.")

    if os.path.exists(args.output):
        confirm = input(f"The file '{args.output}' already exists. Overwrite? (Y/n): ").strip().lower()
        if confirm not in ["y", "yes", ""]: return print("Aborted saving to file.")

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=args.pretty)

    print(f"Saved output to '{args.output}'")

if __name__ == "__main__":
    main()
