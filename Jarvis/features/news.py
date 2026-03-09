import requests
import xml.etree.ElementTree as ET



def get_news():
    url = 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms'
    try:
        news = requests.get(url, timeout=15).text
        root = ET.fromstring(news)
        articles = []
        for item in root.findall('./channel/item')[:10]:
            title = item.findtext('title', default='')
            if title:
                articles.append({'title': title})
        return articles
    except Exception:
        return False


def getNewsUrl():
    return 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms'
