import re
import urllib.parse
import webbrowser


SEARCH_PATTERNS = [
    r"^search\s+google\s+for\s+(.+)$",
    r"^search\s+web\s+for\s+(.+)$",
    r"^web\s+search\s+for\s+(.+)$",
    r"^google\s+(.+)$",
    r"^search\s+for\s+(.+)$",
]


def extract_search_query(command):
    cleaned = (command or "").strip().lower()
    for pattern in SEARCH_PATTERNS:
        match = re.match(pattern, cleaned)
        if match:
            query = match.group(1).strip(" .?!,\t\n")
            if query:
                return query
    return ""


def google_search(command):
    query = extract_search_query(command)
    if not query:
        return False, ""

    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={encoded_query}"
    opened = webbrowser.open(url)
    return opened, query