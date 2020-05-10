import tweepy

def load_api():
    """
    Reads the API keys from file and returns an authorized API
    """
    credentials = ['consumer_api_key', 'consumer_api_key_secret', 'access_token', 'access_token_secret']
    credential_values = {}
    for credential in credentials:
        with open("E:/newsbot_api_credentials/"+credential+".txt") as f:
            credential_values[credential] = f.read()
    auth = tweepy.OAuthHandler(credential_values['consumer_api_key'], credential_values['consumer_api_key_secret']) 
    auth.set_access_token(credential_values['access_token'], credential_values['access_token_secret'])
    api = tweepy.API(auth)
    return api