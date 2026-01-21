import requests

def fetch_wealth_management_news(api_key, query="wealth management firm policy", max_results=5):
    # Example using NewsAPI.org, customize as needed for your preferred service
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&pageSize={max_results}&language=en&apiKey={api_key}"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
        # Structure: [{'title': ..., 'description': ..., 'url': ..., 'publishedAt': ...}]
    except Exception as e:
        articles = []
    return articles

def summarize_article_with_claude(text, api_key, summarize_fn):
    try:
        return summarize_fn(text, api_key)
    except Exception as e:
        return "Summary not available."
