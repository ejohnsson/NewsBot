from tweepy.models import Status as Tweet
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from typing import Iterable

class FakeNewsDetector:
    
    def __init__(self):
        
        self.newsbot_url = 'https://www.unslanted.net/newsbot/'
        self.driver = None
        
    def _start_driver(self):
        """
        Starts a PhantomJS web driver and directs it to https://www.unslanted.net/newsbot/
        """
        self.driver = webdriver.PhantomJS(executable_path='E:/Downloads/phantomjs-2.1.1-windows/phantomjs-2.1.1-windows/bin/phantomjs.exe')
        self.driver.get(self.newsbot_url)
        
    def _reset_driver(self):
        """
        Redirects web driver to https://www.unslanted.net/newsbot/
        """
        self.driver.get(self.newsbot_url)
        
    def _quit_driver(self):
        """
        Kills the web driver
        """
        self.driver.quit()
        
    def _get_proba(self, query_url: str, quit_driver_when_done: bool = False):
        """
        Gets the four probabilities for a given url
        """
        try:
            self._reset_driver()
        except (ConnectionRefusedError, AttributeError):
            self._start_driver()
        
        try:
            # Submit query
            text_box = self.driver.find_element_by_id("id_entryURL")
            text_box.send_keys(query_url)
            text_box.send_keys(Keys.ENTER)
            
        except NoSuchElementException:
            raise Exception("Can't find the text box to write the query")
            
        try:
            # Get probabilities
            probs = tuple(float(self.driver.find_element_by_id(prob).get_attribute('aria-valuenow'))/100 for prob in ['fakeProb_bar', 'MfakeProb_bar', 'MtrueProb_bar', 'trueProb_bar'])
            
        except NoSuchElementException: # Return (-1, -1, -1, -1) if the url doesn't work
            probs = (-1, -1, -1, -1)
        
        if quit_driver_when_done:
            self._quit_driver()
            
        return probs
    
    @staticmethod
    def extract_url(tweet: Tweet) -> str:
        """
        Returns the quoted URL from a given tweet.
        """
        try:
            return tweet.entities['urls'][0]['expanded_url']
        except:
            return None
        
    def predict_proba(self, tweets: Iterable[Tweet]):
        """
        Returns list of tuples with four probabilities. Kills the driver when done
        """
        self._start_driver()
        
        query_urls = list(map(self.extract_url, tweets))
        prob_list = list(map(self._get_proba, query_urls))
        
        self._quit_driver()
        
        return prob_list
