import re
from html.parser import HTMLParser
from typing import Dict, List, Optional, Tuple

class TagParser(HTMLParser):
    """Custom subclass of `HTMLParser` for parsing HTML tags."""
    
    def __init__(self, tag: str, attrs: Dict[str, str], find_all: bool = True, get_attrs: bool = False) -> None:
        """
        Initialize the tag parser with parameters for matching tags.

        :param tag: The regex pattern matching the tag name(s) to search for.
        :type tag: str
        :param attrs: The attribute names, and value matching regex patterns included in the tag.
        :type attrs: dict[str, str]
        :param find_all: Whether to find all matching tags, or only the first one.
        :type find_all: bool
        :param get_attrs: Whether to return matching attributes of the tag instead of its content.
        :type get_attrs: bool
        """
        super().__init__()
        self.tag = re.compile(tag)
        self.attrs = {k: re.compile(v) for k, v in attrs.items()}
        self.find_all = find_all
        self.get_attrs = get_attrs
        self.capture = False
        self.current_data = []
        self.matched = []
        self.stack = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        """
        Handle the start of an HTML tag. Capturing content begins if the tag and its attributes match the criteria.

        :param tag: The name of the encountered tag.
        :type tag: str
        :param attrs: The attribute names and values as a list of tuples.
        :type attrs: list[tuple[str, str | None]]
        """
        # Check if the tag name matches the given pattern
        if self.tag.fullmatch(tag):
            attrs_dict = dict(attrs)

            # Check if all required attributes of the tag are present
            if all(k in attrs_dict and self.attrs[k].search(str(attrs_dict[k])) for k in self.attrs):
                if self.get_attrs:
                    self.matched.append(attrs_dict)

                    # If only the first match is needed, end capturing content
                    if not self.find_all: self.capture = False
                    return
                
                # Begin capturing content
                self.capture = True
                self.stack.append(tag)
                self.current_data.append(f"<{tag}{"".join(f' {k}="{v}"' for k, v in attrs)}>")
            elif self.capture:
                # Capture nested tags by the same name in the matched region
                self.stack.append(tag)
                self.current_data.append(f"<{tag}{"".join(f' {k}="{v}"' for k, v in attrs)}>")
        elif self.capture:
            # Capture nested tags by a differing name in the matched region
            self.stack.append(tag)
            self.current_data.append(f"<{tag}{"".join(f' {k}="{v}"' for k, v in attrs)}>")
    
    def handle_endtag(self, tag: str) -> None:
        """
        Handle the end of an HTML tag. Capturing content ends when the corresponding start tag is closed.

        :param tag: The name of the closing tag.
        :type tag: str
        """
        if self.capture:
            self.current_data.append(f"</{tag}>")

            # Check if the closing tag matches the most recent unclosed tag and close it
            if tag == self.stack[-1]: self.stack.pop()

            # If the stack is empty, no unclosed tags remain
            if not self.stack:
                # Save the captured result and reset
                result = "".join(self.current_data)
                self.matched.append(result)
                self.capture = False
                self.current_data = []

    def handle_data(self, data: str) -> None:
        """
        Handle the text content of the HTML tag. Content is appended to the current capture if inside a matching tag.

        :param data: The text content of the tag.
        :type data: str
        """
        if self.capture: self.current_data.append(data)

def find(html: str, tag: str, attrs: Dict[str, str] = {}) -> str:
    """
    Search the given HTML for the *first* occurrence of a tag matching the specified name and attributes, 
    and return its full content, including nested tags.

    :param html: The HTML string to search.
    :type html: str
    :param tag: The regex pattern matching the tag name(s) to search for.
    :type tag: str
    :param attrs: The attribute names, and value matching regex patterns included in the tag.
    :type attrs: dict[str, str]
    :return: The matched HTML tag in `str` format, including its content and nested tags, or an empty string if no match was found.
    :rtype: str
    """
    parser = TagParser(tag, attrs, find_all=False, get_attrs=False)
    parser.feed(html)

    # Return cleaned result without newlines and tabs
    if parser.matched: return parser.matched[0].replace("\n", "").replace("\t", "").strip()
    
    return ""

def find_all(html: str, tag: str, attrs: Dict[str, str] = {}) -> List[str]:
    """
    Search the given HTML for *all* occurrences of a tag matching the specified name and attributes, 
    and return their full contents, including nested tags.

    :param html: The HTML string to search.
    :type html: str
    :param tag: The regex pattern matching the tag name(s) to search for.
    :type tag: str
    :param attrs: The attribute names, and value matching regex patterns included in the tag.
    :type attrs: dict[str, str]
    :return: The matched HTML tags as a list of strings, including their content and nested tags.
    :rtype: list[str]
    """
    parser = TagParser(tag, attrs, find_all=True, get_attrs=False)
    parser.feed(html)

    return [item.replace("\n", "").replace("\t", "").strip() for item in parser.matched]

def find_text(html: str, tag: str, attrs: Dict[str, str] = {}) -> str:
    """
    Search the given HTML for the *first* occurrence of a tag matching the specified name and attributes, 
    and return its inner text content.

    :param html: The HTML string to search.
    :type html: str
    :param tag: The regex pattern matching the tag name(s) to search for.
    :type tag: str
    :param attrs: The attribute names, and value matching regex patterns included in the tag.
    :type attrs: dict[str, str]
    :return: The inner text content of the matched HTML tag in `str` format, or an empty string if no match was found.
    :rtype: str
    """
    parser = TagParser(tag, attrs, find_all=False, get_attrs=False)
    parser.feed(html)

    # Strip all tags to get the inner text content
    if parser.matched: return re.sub(r"<.*?>", "", parser.matched[0], flags=re.DOTALL)

    return ""

def find_all_text(html: str, tag: str, attrs: Dict[str, str] = {}) -> List[str]:
    """
    Search the given HTML for *all* occurrences of a tag matching the specified name and attributes, 
    and return their inner text content.

    :param html: The HTML string to search.
    :type html: str
    :param tag: The regex pattern matching the tag name(s) to search for.
    :type tag: str
    :param attrs: The attribute names, and value matching regex patterns included in the tag.
    :type attrs: dict[str, str]
    :return: The inner text content of the matched HTML tags as a list of strings.
    :rtype: list[str]
    """
    parser = TagParser(tag, attrs, find_all=True, get_attrs=False)
    parser.feed(html)

    return [re.sub(r"<.*?>", "", item, flags=re.DOTALL) for item in parser.matched]

def find_attrs(html: str, tag: str, attrs: Dict[str, str] = {}) -> Dict[str, str]:
    """
    Search the given HTML for the *first* occurrence of a tag matching the specified name and attributes, 
    and return its attributes.

    :param html: The HTML string to search.
    :type html: str
    :param tag: The regex pattern matching the tag name(s) to search for.
    :type tag: str
    :param attrs: The attribute names, and value matching regex patterns included in the tag.
    :type attrs: dict[str, str]
    :return: The attributes of the matched HTML tag in `dict` format, with keys and values in `str` format.
    :rtype: dict[str, str]
    """
    parser = TagParser(tag, attrs, find_all=False, get_attrs=True)
    parser.feed(html)

    return parser.matched[0] if parser.matched else {}

def find_all_attrs(html: str, tag: str, attrs: Dict[str, str] = {}) -> List[Dict[str, str]]:
    """
    Search the given HTML for *all* occurrences of a tag matching the specified name and attributes, 
    and return their attributes.

    :param html: The HTML string to search.
    :type html: str
    :param tag: The regex pattern matching the tag name(s) to search for.
    :type tag: str
    :param attrs: The attribute names, and value matching regex patterns included in the tag.
    :type attrs: dict[str, str]
    :return: The attributes of the matched HTML tags as a list of dictionaries.
    :rtype: list[dict[str, str]]
    """
    parser = TagParser(tag, attrs, find_all=True, get_attrs=True)
    parser.feed(html)

    return parser.matched
