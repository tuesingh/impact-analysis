import feedparser
import requests
from datetime import datetime
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecRSSConnector:
    BASE_URL = "https://www.sec.gov/cgi-bin/browse-edgar"
    PRESS_RELEASE_FEED = "https://www.sec.gov/rss/litigation/press-release.xml"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'RiskIntelligence/1.0'})
    
    def fetch_press_releases(self) -> List[Dict]:
        items = []
        try:
            feed = feedparser.parse(self.PRESS_RELEASE_FEED)
            logger.info(f"Fetched SEC feed with {len(feed.entries)} entries")
            for entry in feed.entries:
                item = {
                    'source': 'SEC',
                    'type': 'press_release',
                    'title': entry.get('title', 'N/A'),
                    'summary_raw': entry.get('summary', ''),
                    'published_at': entry.get('published', datetime.now().isoformat()),
                    'url': entry.get('link', ''),
                    'tags': self._extract_tags(entry.get('summary', '')),
                    'entities': [],
                }
                items.append(item)
        except Exception as e:
            logger.error(f"Error: {e}")
        return items
    
    def _extract_tags(self, text: str) -> List[str]:
        keywords = ['investment adviser', 'broker-dealer', 'AML', 'custody']
        return [kw for kw in keywords if kw.lower() in text.lower()]

class FinraConnector:
    RSS_FEED = "https://www.finra.org/feeds/news-and-events"
    
    def __init__(self):
        self.session = requests.Session()
    
    def fetch_notices(self) -> List[Dict]:
        items = []
        try:
            feed = feedparser.parse(self.RSS_FEED)
            logger.info(f"Fetched FINRA feed")
            for entry in feed.entries:
                item = {
                    'source': 'FINRA',
                    'type': 'notice',
                    'title': entry.get('title', 'N/A'),
                    'summary_raw': entry.get('summary', ''),
                    'published_at': entry.get('published', datetime.now().isoformat()),
                    'url': entry.get('link', ''),
                    'tags': [],
                    'entities': [],
                }
                items.append(item)
        except Exception as e:
            logger.error(f"Error: {e}")
        return items

class FedRegConnector:
    API_BASE = "https://www.federalregister.gov/api/v1"
    AGENCIES = ['SEC', 'DOL']
    KEYWORDS = ['investment adviser', 'broker-dealer']
    
    def __init__(self):
        self.session = requests.Session()
    
    def fetch_regulations(self) -> List[Dict]:
        items = []
        for agency in self.AGENCIES:
            for keyword in self.KEYWORDS:
                try:
                    params = {'agencies': agency, 'search': keyword, 'per_page': 5, 'format': 'json'}
                    resp = self.session.get(f"{self.API_BASE}/documents", params=params, timeout=10)
                    resp.raise_for_status()
                    data = resp.json()
                    for doc in data.get('results', []):
                        item = {
                            'source': 'FedReg',
                            'type': 'rule',
                            'title': doc.get('title', 'N/A'),
                            'summary_raw': doc.get('abstract', ''),
                            'published_at': doc.get('publication_date', datetime.now().isoformat()),
                            'url': doc.get('html_url', ''),
                            'tags': [keyword],
                            'entities': [agency],
                        }
                        items.append(item)
                except Exception as e:
                    logger.error(f"Error: {e}")
        return items
