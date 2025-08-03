import re
import json
import urllib.request
import sanakirja.tag_parser as tag_parser
from enum import IntEnum
from urllib.parse import quote
from typing import Dict, List, Optional, Tuple, TypedDict, Union

# Custom type aliases for improved readability
StrDictList = List[Dict[str, str]]
OptStrDictList = List[Dict[str, Optional[str]]]
TranslationEntry = Dict[str, Optional[Union[str, List[str], OptStrDictList]]]

ExampleResult = Dict[str, List[str]]
PronunciationResult = Dict[str, OptStrDictList]
TranslationResult = Dict[str, List[TranslationEntry]]
DefinitionResult = List[Optional[Union[str, List[str], Dict[str, str]]]]

class SanakirjaResult(TypedDict):
    """Result dictionary with type annotated individual fields."""
    id: int
    url: str
    source_language: Optional[str]
    target_language: Optional[str]
    word: str
    transliteration: Optional[str]
    gender: Optional[str]
    additional_source_languages: Dict[str, str]
    relations: StrDictList
    did_you_mean: Dict[str, str]
    suggestions: OptStrDictList
    found_examples: OptStrDictList
    alternative_spellings: OptStrDictList
    multiple_spellings: StrDictList
    synonyms: OptStrDictList
    pronunciations: PronunciationResult
    abbreviations: OptStrDictList
    inflections: StrDictList
    definitions: DefinitionResult
    examples: ExampleResult
    categories: StrDictList
    translations: TranslationResult

class LangCodes(IntEnum):
    """Map ISO 3166-2 format country codes to integer values used by sanakirja.org."""
    bg = 1
    et = 2
    en = 3
    es = 4
    eo = 5
    it = 6
    el = 7
    la = 8
    lv = 9
    lt = 10
    no = 11
    pt = 12
    pl = 13
    fr = 14
    sv = 15
    de = 16
    fi = 17
    da = 18
    cs = 19
    tr = 20
    hu = 21
    ru = 22
    nl = 23
    jp = 24

class LanguageCodeError(ValueError):
    """Exception class for invalid language codes."""

    def __init__(self, lang: str) -> None:
        """
        Initialize the invalid language code exception.

        :param lang: The invalid language code.
        :type lang: str
        """
        super().__init__(f"Invalid language code: '{lang}'")

class Sanakirja:
    """Class for fetching information from sanakirja.org."""

    def __init__(self) -> None:
        """Initialize the Sanakirja object with the base URL."""

        self.__base_url = "https://www.sanakirja.org/search.php?q={}&l={}&l2={}"

    @staticmethod
    def _validate_lang_code(lang: Union[int, str, LangCodes]) -> Union[int, bool]:
        """
        Validate the given language code.

        :param lang: The language code to validate.
        :type lang: int | str | LangCodes
        :return: The validated language code in `int` format, or `False` if invalid.
        :rtype: int | bool
        """
        if lang == 0: return 0
        elif isinstance(lang, str) and hasattr(LangCodes, lang.lower()): return LangCodes[lang.lower()]
        elif isinstance(lang, int) and lang in LangCodes._value2member_map_: return lang
        elif isinstance(lang, LangCodes): return lang
        return False
    
    @staticmethod
    def _validate_result_lang_code(lang: Union[int, str, LangCodes]) -> Union[str, bool]:
        """
        Validate the given result language code.

        :param lang: The result language code to validate.
        :type lang: int | str | LangCodes
        :return: The validated result language code in `str` format, or `False` if invalid.
        :rtype: str | bool
        """
        valid_langs = ["en", "fi", "fr", "sv"]

        if isinstance(lang, str) and lang.lower() in valid_langs: return lang.lower()
        elif isinstance(lang, int) and lang in LangCodes._value2member_map_ and (lang_name := LangCodes(lang).name) in valid_langs: return lang_name
        elif isinstance(lang, LangCodes) and lang.name in valid_langs: return lang.name
        return False
    
    @staticmethod
    def _get_sk_var(html: str) -> Dict[str, Union[int, str, bool]]:
        """
        Resolve the SK object from the HTML of the webpage.

        :param html: The HTML of the webpage.
        :type html: str
        :return: The resolved SK object in `dict` format, with keys in `str` format and values in `int`, `str` or `bool` format.
        :rtype: dict[str, int | str | bool]
        """
        body = tag_parser.find(html, "body")
        sk_var = tag_parser.find_text(body, "script")
        sk_var_dict = json.loads(sk_var.split("var SK=")[-1][:-1])

        return sk_var_dict
    
    @staticmethod
    def _get_multiple_spellings(html: str) -> StrDictList:
        """
        Extract the multiple spellings from the HTML of the webpage.

        :param html: The HTML of the webpage.
        :type html: str
        :return: The multiple spellings as :type:`StrDictList` type.
        :rtype: StrDictList
        """
        multiple_spellings_ul = tag_parser.find(html, "ul", {"class": "multiple_spellings"})
        multiple_spellings = []

        for li in tag_parser.find_all(multiple_spellings_ul, "li"):
            word = tag_parser.find_text(li, "a")
            url = f"https://sanakirja.org{href}" if (href := tag_parser.find_attrs(li, "a").get("href", "")) else None

            multiple_spellings.append({"word": word, "word_url": url})

        return multiple_spellings
        
    @staticmethod
    def _get_alt_synonyms_and_pronunciations(html: str) -> Tuple[OptStrDictList, OptStrDictList, PronunciationResult]:
        """
        Extract the alternative spellings, synonyms and pronunciations from the HTML of the webpage.

        :param html: The HTML of the webpage.
        :type html: str
        :return: The alternative spellings and synonyms as :type:`OptStrDictList` type and pronunciations as :type:`PronunciationResult` type.
        :rtype: tuple[OptStrDictList, OptStrDictList, PronunciationResult]
        """
        lists_div = tag_parser.find(html, "div", {"class": "lists"})
        alternative_spellings_div = tag_parser.find(lists_div, "div", {"class": "alternative_spellings"})
        alternative_spellings = []

        for li in tag_parser.find_all(alternative_spellings_div, "li"):
            word = tag_parser.find_text(li, "a")
            url = f"https://www.sanakirja.org/{href}" if (href := tag_parser.find_attrs(li, "a").get("href", "")) else None
            context = tag_parser.find_text(li, "span").strip("() ") or None

            alternative_spellings.append({"word": word, "context": context, "word_url": url})

        synonyms_div = tag_parser.find(lists_div, "div", {"class": "synonyms"})
        synonyms = []

        for li in tag_parser.find_all(synonyms_div, "li"):
            word = tag_parser.find_text(li, "a")
            url = f"https://www.sanakirja.org/{href}" if (href := tag_parser.find_attrs(li, "a").get("href", "")) else None
            context = tag_parser.find_text(li, "span").strip("() ") or None

            synonyms.append({"word": word, "context": context, "word_url": url})

        pronunciations_div = tag_parser.find(lists_div, "div", {"class": "pronunciation"})
        pronunciations = {}

        for pronunciation in tag_parser.find_all(pronunciations_div, "li"):
            # Convert "Tuntematon aksentti" to "unknown" to unify key names
            abbr = tag_parser.find_text(pronunciation, "abbr").lower()
            if not abbr or abbr == "tuntematon aksentti": abbr = "unknown"

            url = tag_parser.find_attrs(pronunciation, "a", {"class": "audio"}).get("href", "").lstrip("//") or None
            pronunciation_ul = tag_parser.find(pronunciation, "ul")

            if pronunciation_ul:
                for li in tag_parser.find_all(pronunciation_ul, "li"):
                    text = tag_parser.find_text(li, "span") or None
                    pronunciations.setdefault(abbr, []).append({"text": text, "audio_url": url})
            else:
                pronunciations.setdefault(abbr, []).append({"text": None, "audio_url": url})

        return alternative_spellings, synonyms, pronunciations
    
    @staticmethod
    def _get_source_languages(html: str) -> Dict[str, str]:
        """
        Extract the additional source languages from the HTML of the webpage.

        :param html: The HTML of the webpage.
        :type html: str
        :return: The additional source languages in `dict` format, with keys and values in `str` format.
        :rtype: dict[str, str]
        """
        source_languages_div = tag_parser.find(html, "div", {"id": "source_languages"})
        source_languages = {}

        # Omit the current language
        for li in tag_parser.find_all(source_languages_div, "li")[1:]:
            href = tag_parser.find_attrs(li, "a").get("href", "")
            lang_match = re.search(r"l=(\d{1,2})", href)
            lang = int(lang_match.group(1) if lang_match else 0)
            url = f"https://www.sanakirja.org{href}" if href else None

            source_languages[LangCodes(lang).name] = url

        return source_languages
    
    @staticmethod
    def _get_abbreviations(html: str) -> OptStrDictList:
        """
        Extract the abbreviations from the HTML of the webpage.

        :param html: The HTML of the webpage.
        :type html: str
        :return: The abbreviations as :type:`OptStrDictList` type.
        :rtype: OptStrDictList
        """
        abbreviations_div = tag_parser.find(html, "div", {"class": "abbreviations"})
        abbreviations = []

        for li in tag_parser.find_all(abbreviations_div, "li"):
            word = tag_parser.find_text(li, "a")
            url = f"https://www.sanakirja.org/{href}" if (href := tag_parser.find_attrs(li, "a").get("href", "")) else None
            context = tag_parser.find_text(li, "li").rstrip(word).strip("() ") or None

            abbreviations.append({"word": word, "context": context, "word_url": url})

        return abbreviations
    
    @staticmethod
    def _get_inflections(html: str) -> StrDictList:
        """
        Extract the inflections from the HTML of the webpage.

        :param html: The HTML of the webpage.
        :type html: str
        :return: The inflections as :type:`StrDictList` type.
        :rtype: StrDictList
        """
        inflections_table = tag_parser.find(html, "table", {"class": "inflections"})
        inflections, inflections_pairs = [], []

        for row in tag_parser.find_all(inflections_table, "tr", {"class": r"sk-row[12]"}):
            text = [text for text in tag_parser.find_all_text(row, "td") if text]
            hrefs = [attrs.get("href", "") for attrs in tag_parser.find_all_attrs(row, "a")]
            urls = [f"https://www.sanakirja.org/{href}" if href else None for href in hrefs]

            for i in range(len(text)):
                inflections_pairs.append(text[i] if not i % 2 else (text[i], urls[i // 2]))

        for i in range(0, len(inflections_pairs), 2):
            inflection_type = inflections_pairs[i]
            word, url = inflections_pairs[i + 1]
            
            inflections.append({
                "type": inflection_type,
                "word": word,
                "word_url": url
            })

        return inflections
    
    @staticmethod
    def _get_translations(html: str, l2: int) -> TranslationResult:
        """
        Extract the translations to the target language from the HTML of the webpage.

        :param html: The HTML of the webpage.
        :type html: str
        :param l2: The target language.
        :type l2: int
        :return: The translations as :type:`TranslationResult` type.
        :rtype: TranslationResult
        """
        translations_table = tag_parser.find(html, "table", {"class": "translations"})

        if not l2:
            rows_tr = tag_parser.find_all(translations_table, "tr", {"class": r"sk-row[12]"})
            lang_dict = {}

            for row in rows_tr:
                rows_td = tag_parser.find_all(row, "td")
                lang_tag = tag_parser.find(rows_td[0], "a")
                lang = int(tag_parser.find_attrs(lang_tag, "a").get("href", "").split("=")[-1] or 0)
                words_and_transliterations = []

                for full_word in rows_td[1].split(","):
                    word = tag_parser.find_text(full_word, "a")
                    url = f"https://www.sanakirja.org{href}" if (href := tag_parser.find_attrs(full_word, "a").get("href", "")) else None
                    transliteration_match = re.search(r"\(([^)]+)\)", full_word)
                    transliteration = transliteration_match.group(1) if transliteration_match else None

                    words_and_transliterations.append((word, transliteration, url))

                lang_dict[LangCodes(lang).name] = [{
                    "word": word,
                    "transliteration": transliteration,
                    "gender": None,
                    "group": None,
                    "word_url": url,
                    "context": [],
                    "pronunciations": {}
                } for word, transliteration, url in words_and_transliterations]

            return lang_dict

        rows_tr = tag_parser.find_all(translations_table, "tr", {"class": r"(group_name|sk-row[12])"})
        current_group = None
        translations = []

        for row in rows_tr:
            if "group_name" in row:
                current_group = tag_parser.find_text(row, "td")
                continue

            rows_td = tag_parser.find_all(row, "td")
            word = tag_parser.find_text(rows_td[1], "a")
            url = f"https://www.sanakirja.org{href}" if (href := tag_parser.find_attrs(rows_td[1], "a").get("href", "")) else None
            
            gender_span = tag_parser.find_text(rows_td[1], "span")
            gender = gender_span.strip("{}") if gender_span else None

            transliterations = re.search(r"\(([^)]+)\)", tag_parser.find_text(rows_td[1], "td"))
            transliteration = transliterations.group(1) if transliterations else None

            # The 3rd "td" tag is *usually* reserved for context, however, sometimes it contains pronunciations instead
            # For this reason, we have to check if it contains nested tags
            context_td = tag_parser.find_text(rows_td[2] if len(rows_td) > 2 else "", "td")
            context = [part.strip() for part in context_td.split(",")] if context_td and "<" not in re.sub(r"^<td>|</td>$", "", rows_td[2]) else []

            pronunciation_ul = tag_parser.find(row, "ul", {"class": "audio"})
            pronunciation_li = tag_parser.find_all(pronunciation_ul, "li")
            abbrs = [abbr.lower() or "unknown" for abbr in tag_parser.find_all_text(pronunciation_ul, "li")]
            pronunciations = {}

            for abbr, li in zip(abbrs, pronunciation_li):
                audio_url = tag_parser.find_attrs(li, "a", {"class": "audio"}).get("href", "").lstrip("//") or None
                pronunciations.setdefault(abbr, []).append(audio_url)

            translations.append({
                "word": word,
                "transliteration": transliteration,
                "gender": gender,
                "group": current_group,
                "word_url": url,
                "context": context,
                "pronunciations": pronunciations
            })

        return {LangCodes(l2).name: translations} if translations else {}
    
    @staticmethod
    def _get_transliteration(html: str) -> Optional[str]:
        """
        Extract the transliteration from the HTML of the webpage.

        :param html: The HTML of the webpage.
        :type html: str
        :return: The transliteration in `str` format, or None if not applicable.
        :rtype: str | None
        """
        transliteration_text = tag_parser.find_text(html, "p", {"class": "transliteration"})
        transliteration = transliteration_text.lstrip("Translitterointi: ")[:-1] if transliteration_text else None

        return transliteration
    
    @staticmethod
    def _get_gender(html: str) -> Optional[str]:
        """
        Extract the gender from the HTML of the webpage.

        :param html: The HTML of the webpage.
        :type html: str
        :return: The gender in `str` format, or None if not applicable.
        :rtype: str | None
        """
        gender_p = tag_parser.find(html, "p", {"class": "gender"})
        gender = tag_parser.find_text(gender_p, "span") or None

        return gender
    
    @staticmethod
    def _get_relations(html: str) -> StrDictList:
        """
        Extract the relations from the HTML of the webpage.

        :param html: The HTML of the webpage.
        :type html: str
        :return: The relations as :type:`StrDictList` type.
        :rtype: StrDictList
        """
        relations_div = tag_parser.find(html, "ul", {"class": r"relations.*"})
        relations, unique_words = [], set()

        for li in tag_parser.find_all(relations_div, "li"):
            word = tag_parser.find_text(li, "a")
            url = f"https://www.sanakirja.org/{href}" if (href := tag_parser.find_attrs(li, "a").get("href", "")) else None
        
            if word not in unique_words:
                relations.append({"word": word, "word_url": url})
                unique_words.add(word)

        return relations
    
    @staticmethod
    def _get_dym_suggestions_and_found_examples(html: str) -> Tuple[Dict[str, str], OptStrDictList, OptStrDictList]:
        """
        Extract the similar words from the HTML of the webpage.

        :param html: The HTML of the webpage.
        :type html: str
        :return: The similar words as :type:`OptStrDictList` type.
        :rtype: tuple[dict[str, str], OptStrDictList, OptStrDictList]
        """
        similar_words_div = tag_parser.find(html, "div", {"class": "similar_words"})
        suggestions_ul = tag_parser.find(similar_words_div, "ul", {"id": "suggestions"})
        suggestions_and_font_sizes = []

        for li in tag_parser.find_all(suggestions_ul, "li"):
            word = tag_parser.find_text(li, "a")
            corrected_word = tag_parser.find_text(li, "li").lstrip(word).replace("->", "").strip() or None

            attrs = tag_parser.find_attrs(li, "a")
            url = f"https://www.sanakirja.org/{href}" if (href := attrs.get("href", "")) else None
            font_size = int(style.split()[-1].rstrip("%;") if (style := attrs.get("style", "")) else 100)

            suggestions_and_font_sizes.append(({"word": word, "corrected_word": corrected_word, "word_url": url}, font_size))

        # Place the words in descending order by their font sizes
        suggestions = [words for words, _ in sorted(suggestions_and_font_sizes, key=lambda x: x[1], reverse=True)]

        did_you_mean = {}

        if (did_you_mean_h2 := tag_parser.find(similar_words_div, "h2", {"class": "did_you_mean"})):
            did_you_mean_word = tag_parser.find_text(did_you_mean_h2, "a")
            did_you_mean_url = f"https://www.sanakirja.org/{href}" if (href := tag_parser.find_attrs(did_you_mean_h2, "a").get("href", "")) else None

            did_you_mean = {"word": did_you_mean_word, "word_url": did_you_mean_url}

        examples_ul = tag_parser.find(similar_words_div, "ul", {"class": "examples"})
        found_examples = []

        for li in tag_parser.find_all(examples_ul, "li"):
            word = tag_parser.find_text(li, "a")
            example = tag_parser.find_text(li, "li").lstrip(f"{word} - ").strip() or None
            url = f"https://www.sanakirja.org/{href}" if (href := tag_parser.find_attrs(li, "a").get("href", "")) else None

            found_examples.append({"word": word, "text": example, "word_url": url})

        return did_you_mean, suggestions, found_examples
    
    @staticmethod
    def _get_definitions(html: str) -> DefinitionResult:
        """
        Extract the definitions from the HTML of the webpage.

        :param html: The HTML of the webpage.
        :type html: str
        :return: The definitions as :type:`DefinitionResult` type.
        :rtype: DefinitionResult
        """
        definitions_div = tag_parser.find(html, "div", {"class": "definitions"})
        current_group = None
        definitions = []

        for li in tag_parser.find_all(definitions_div, r"li|h4"):
            if "h4" in li:
                current_group = tag_parser.find_text(li, "h4")
                continue

            context_em = tag_parser.find_text(li, "em").strip("()")
            context = [part.strip() for part in context_em.split(",")] if context_em else []
            text_full = tag_parser.find_text(li, "li")

            # Account for the stripped parentheses and whitespace
            text = text_full[len(context_em) + 3:] if context_em else text_full

            search_words = tag_parser.find_all_text(li, "a")
            hrefs = [attrs.get("href", "") for attrs in tag_parser.find_all_attrs(li, "a")]
            urls = [f"https://www.sanakirja.org/{href}" if href else None for href in hrefs]

            words = [{"word": word, "word_url": url} for word, url in zip(search_words, urls)]

            definitions.append({"text": text, "group": current_group, "context": context, "words": words})

        return definitions
    
    @staticmethod
    def _get_examples(html: str, l: int, l2: int) -> ExampleResult:
        """
        Extract the examples from the HTML of the webpage.

        :param html: The HTML of the webpage.
        :type html: str
        :return: The examples as :type:`ExampleResult` type.
        :rtype: ExampleResult
        """
        examples_div = tag_parser.find(html, "div", {"class": "examples"})
        examples_li = tag_parser.find_all(examples_div, "li")
        examples = tag_parser.find_all_text(examples_div, "li")
        translated_examples = [example for li in examples_li if (example := tag_parser.find_text(li, "ul"))]

        for i, translation in enumerate(translated_examples):
            examples[i] = examples[i].replace(translation, "")

        result = {}
        if examples: result[LangCodes(l).name] = examples
        if translated_examples: result[LangCodes(l2).name] = translated_examples

        return result
    
    @staticmethod
    def _get_categories(html: str) -> StrDictList:
        """
        Extract the categories from the HTML of the webpage.

        :param html: The HTML of the webpage.
        :type html: str
        :return: The categories as :type:`StrDictList` type.
        :rtype: StrDictList
        """
        categories_div = tag_parser.find(html, "div", {"class": "categories"})
        categories = []

        for li in tag_parser.find_all(categories_div, "li"):
            text = tag_parser.find_text(li, "a")
            url = f"https://www.sanakirja.org{href}" if (href := tag_parser.find_attrs(li, "a").get("href", "")) else None

            categories.append({"text": text, "category_url": url})

        return categories
    
    def search(self, q: str, l: Union[int, str, LangCodes] = 0, l2: Union[int, str, LangCodes] = 0, ui_lang: Union[int, str, LangCodes] = "fi") -> SanakirjaResult:
        """
        Search sanakirja.org for information on a given query.

        :param q: The search query to retrieve information for.
        :type q: str
        :param l: The source language.
        :type l: int | str | LangCodes
        :param l2: The target language.
        :type l2: int | str | LangCodes
        :param ui_lang: The language of user interface elements.
        :type ui_lang: int | str | LangCodes
        :return: The information dictionary as a :type:`SanakirjaResult` type.
        :rtype: SanakirjaResult
        :raises LanguageCodeError: If either of the given language codes is invalid.
        """
        if (valid_l := self._validate_lang_code(l)) is False: raise LanguageCodeError(str(l))
        l = valid_l

        if (valid_l2 := self._validate_lang_code(l2)) is False: raise LanguageCodeError(str(l2))
        l2 = valid_l2

        # An invalid result language code gets automatically resolved to "fi", but we will set it explicitly
        if (valid_res_lang := self._validate_result_lang_code(ui_lang)): ui_lang = valid_res_lang or "fi"

        # Create and make a request to the percent-encoded URL
        req = urllib.request.Request(url := self.__base_url.format(quote(q), l, l2), headers={"Cookie": f"ui_lang={ui_lang}"})

        with urllib.request.urlopen(req) as response:
            html = response.read().decode("utf-8")

        sk_var = self._get_sk_var(html)
        if not l: l = sk_var.get("source_language") or 0

        alternative_spellings, synonyms, pronunciations = self._get_alt_synonyms_and_pronunciations(html)
        additional_source_languages = self._get_source_languages(html)
        multiple_spellings = self._get_multiple_spellings(html)
        abbreviations = self._get_abbreviations(html)
        inflections = self._get_inflections(html)
        translations = self._get_translations(html, l2)
        transliteration = self._get_transliteration(html)
        gender = self._get_gender(html)
        relations = self._get_relations(html)
        did_you_mean, suggestions, found_examples = self._get_dym_suggestions_and_found_examples(html)
        definitions = self._get_definitions(html)
        examples = self._get_examples(html, int(l), l2 if not (keys := list(translations.keys())) else LangCodes[keys[0]])
        categories = self._get_categories(html)

        result: SanakirjaResult = {
            "id": int(sk_var.get("main_word_id") or 0),
            "url": url,
            "source_language": (l if isinstance(l, str) else LangCodes(l).name) if l else None,
            "target_language": (l2 if isinstance(l2, str) else LangCodes(l2).name) if l2 else None,
            "word": str(sk_var.get("main_word_text") or q),
            "transliteration": transliteration,
            "gender": gender,
            "additional_source_languages": additional_source_languages,
            "relations": relations,
            "did_you_mean": did_you_mean,
            "suggestions": suggestions,
            "found_examples": found_examples,
            "alternative_spellings": alternative_spellings,
            "multiple_spellings": multiple_spellings,
            "synonyms": synonyms,
            "pronunciations": pronunciations,
            "abbreviations": abbreviations,
            "inflections": inflections,
            "definitions": definitions,
            "examples": examples,
            "categories": categories,
            "translations": translations
        }
        return result
