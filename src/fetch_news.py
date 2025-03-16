# src/fetch_news.py
import requests
import logging

def fetch_headlines(api_key, query, from_date=None, to_date=None):
    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': query,
        'apiKey': api_key,
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 100  # Maximum articles per request
    }
    if from_date:
        params['from'] = from_date
    if to_date:
        params['to'] = to_date

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return [article['title'] for article in data.get('articles', [])]
    else:
        logging.error(f"Failed to fetch news: {response.status_code} - {response.text}")
        return []