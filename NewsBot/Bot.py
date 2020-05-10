import tweepy
import webbrowser
import datetime
from NewsBot.TweetManager import read_tweets as rt
from NewsBot.PublicModels import FakeNewsDetector


# NewsBot Twitter handle
MY_SCREEN_NAME = "NewsBot_io"


class Bot:
    
    def __init__(self):
        
        self.following = []  # List of screen names (Twitter handles)
        self.tweets_to_reply_to = []  # List of 'Status' objects (Tweets)
        self.tweet_probs = []  # List of tuples, e.g. [(.05, .2, .3, .45)]
        
    def get_tweets_to_reply_to(self, max_n_days: int, include_replies: bool = False, save_tweets: bool = True, return_tweets: bool = False):
        """
        Retrieves a list of all the tweets that our bot can reply to.
        WARNING: If 'save_tweets' is True, overwrites self.tweets_to_reply_to
        """
        tweets_to_reply_to = []
        
        # Get all accounts the bot is following
        following = rt.get_my_following()
        
        # Get the most recent tweets from each of those accounts
        for screen_name in following:
            tweets_to_reply_to += rt.get_user_tweets(screen_name=screen_name,
                                                     include_replies=include_replies,
                                                     max_n_days=max_n_days)
            
        # Filter out non-news
        tweets_to_reply_to = list(filter(rt.is_news, tweets_to_reply_to))
            
        # Filter out tweets that have already been replied to
        tweets_to_reply_to = list(filter(lambda t: not rt.already_replied(t), tweets_to_reply_to))
        
        if save_tweets:
            self.following = following
            self.tweets_to_reply_to = tweets_to_reply_to
        
        if return_tweets:
            return tweets_to_reply_to
        
    def get_tweet_probs(self, save_probs: bool = True, return_probs: bool = False):
        """
        Computes the four probabilities for each tweet
        """
        assert len(self.tweets_to_reply_to) > 0, "There are no tweets to reply to."
                
        # Get predictions
        model = FakeNewsDetector()
        tweet_probs = model.predict_proba(self.tweets_to_reply_to)
        
        if save_probs:
            self.tweet_probs = tweet_probs
        
        if return_probs:
            return self.tweet_probs
        
    def get_days_since_last_tweet(self):
        """
        Return the number of days since this bot last tweeted, or -1 if it has never tweeted
        """
        col_id = 3  # Column ID of datetime of bot's last tweet
        current_date = datetime.datetime.now()
        try:
            with open('./TweetManager/logs/tweets.csv', 'r') as tweet_log:
                for last_tweet in tweet_log:
                    pass
                last_tweet_date = last_tweet.split(',')[3]
            return (current_date - last_tweet_date).days
        
        except FileNotFoundError:
            return -1
                     
    @staticmethod
    def view_tweet(tweet: tweepy.models.Status):
        """
        Opens web browser to the given tweet
        """
        tweet_id = tweet.id_str
        tweet_screen_name = tweet.user.screen_name
        webbrowser.open("https://twitter.com/{}/status/{}".format(tweet_screen_name, tweet_id), new=0)
        
    def update(self, max_n_days: int = None, include_replies: bool = False):
        """
        Populates all fields needed to post tweets
        Args:
            max_n_days: The number of days in the past to search for tweets
                If 'None', will default to the number of days since the bot's last tweet
            include_replies: If True, will include tweet replies in its search for news articles
        """
        if max_n_days is None:
            max_n_days = self.get_days_since_last_tweet()
            
        # Get tweets to reply to
        self.get_tweets_to_reply_to(max_n_days=max_n_days, include_replies=include_replies, save_tweets=True)
        
        # Get probabilities
        self.get_tweet_probs(save_probs=True)
        
    def post(self, clear_memory: bool = True):
        """
        TODO: This function must post a reply to each tweet in self.tweets_to_reply_to and save the tweet in logs/tweet.csv
              This function will be implemented once my Twitter Developer application is approved.
        """
        
        if clear_memory:
            self.following = []
            self.tweets_to_reply_to = []
            self.tweet_probs = []
            
        pass