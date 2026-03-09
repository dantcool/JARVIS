import webbrowser

def website_opener(domain):
    try:
        value = domain.strip().lower()
        if not value:
            return False

        known_sites = {
            'youtube': 'https://www.youtube.com',
            'google': 'https://www.google.com',
            'github': 'https://www.github.com',
            'reddit': 'https://www.reddit.com',
            'stackoverflow': 'https://stackoverflow.com',
        }
        if value in known_sites:
            url = known_sites[value]
        elif value.startswith('http://') or value.startswith('https://'):
            url = value
        elif '.' in value:
            url = 'https://' + value
        else:
            url = 'https://www.' + value + '.com'

        webbrowser.open(url)
        return True
    except Exception as e:
        print(e)
        return False