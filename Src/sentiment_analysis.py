# src/sentiment_analysis.py
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging

def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = analyzer.polarity_scores(text)
    return sentiment_scores

def aggregate_sentiment(sentiments):
    compound_scores = [s['compound'] for s in sentiments]
    average_sentiment = sum(compound_scores) / len(compound_scores) if compound_scores else 0
    return average_sentiment