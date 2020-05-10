import tweepy
import datetime
from NewsBot.TweetManager import api_manager
import os

# Load api credentials
api = api_manager.load_api()

# NewsBot Twitter handle
MY_SCREEN_NAME = "NewsBot_io"


def is_news(tweet: tweepy.models.Status):
    """
    Returns 1 if the tweet contains a link to a news article, 0 otherwise
    TODO:
        - Will fail if tweet is a retweet, or if link directs to a twitter post which contains the true link
    """
    try:
        link = tweet.entities['urls'][0].get('expanded_url') # Assumes only one link in a post
    except IndexError:
        return False

    # Load news sites
    with open("NewsBot/TweetManager/news_sites.txt", "r") as file:
        news_sites = file.read().splitlines()
        
    # If link contains a news site, return True
    if len(list(filter(lambda site: site in link, news_sites))) > 0:
        return True
    return False


def already_replied(tweet: tweepy.models.Status):
    """
    Returns 1 if the bot has already replied to this tweet, 0 otherwise
    """
    
    tweet_id = tweet.id_str

    try:
        with open('./logs/tweets.csv', 'r') as tweet_log:
            for past_tweet in tweet_log:
                if tweet_id in past_tweet:
                    return True
                
    finally:  # Return false if log file does not exist
        return False
    
    
def get_my_following():
    """
    Return list of accounts that the bot follows
    """
    return [user.screen_name for user in tweepy.Cursor(api.friends, screen_name=MY_SCREEN_NAME).items()]


def is_not_reply(tweet: tweepy.models.Status):
    """
    Returns 1 if tweet is reply, 0 otherwise
    """
    return tweet.in_reply_to_status_id is None


def get_user_tweets(screen_name: str, include_replies: bool = False,  max_n_tweets: int = None, max_n_days: int = None):
    """
    Returns recent tweets from account 'screen_name'
    """
    assert max_n_tweets is not None or max_n_days is not None, "Must specify at least one of 'max_n_tweets' and 'max_n_days'"
    
    if max_n_tweets is None:
        max_n_tweets = 256
    if max_n_days is None:
        max_n_days = 30
        
    # Retrieve tweets
    tweets = api.user_timeline(screen_name=screen_name, count=max_n_tweets*3)
    
    # Remove tweets beyond max_n_days
    now = datetime.datetime.now()
    tweets = list(filter(lambda tweet: (now - tweet.created_at).days <= max_n_days, tweets))
    
    # Remove replies, if necessary
    if not include_replies:
        tweets = list(filter(is_not_reply, tweets))
    
    # Remove extraneous tweets
    if len(tweets) > max_n_tweets:
        tweets = tweets[:max_n_tweets]
        
    return tweets
