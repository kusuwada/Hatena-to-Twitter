#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import requests
import tweepy
import yaml
import unicodedata
from logging import getLogger, config
from article import Article

with open('log_config.yml', 'r') as f:
        log_config = yaml.safe_load(f.read())
        config.dictConfig(log_config)
logger = getLogger(__name__)

class Twitter:

    work_path = None
    TWITTER_TEXT_LIMIT = 280
    
    def __init__(self):
        self.api = None     # for media
        self.client = None  # for tweet
    
    def auth(self):
        try:
            auth = tweepy.OAuthHandler(os.environ['TW_API_KEY'], os.environ['TW_API_KEY_SECRET'])
            auth.set_access_token(os.environ['TW_ACCESS_TOKEN'], os.environ['TW_ACCESS_TOKEN_SECRET'])
            self.api = tweepy.API(auth)
            self.client = tweepy.Client(
                consumer_key        = os.environ['TW_API_KEY'],
                consumer_secret     = os.environ['TW_API_KEY_SECRET'],
                access_token        = os.environ['TW_ACCESS_TOKEN'],
                access_token_secret = os.environ['TW_ACCESS_TOKEN_SECRET'],
            )
        except Exception as e:
            logger.error('ERROR in Authentication')
            logger.error(e)
            raise(e)
        return

    def fetch_image(self, image_url, date, num):
        img_data = requests.get(image_url).content
        output_path = self.work_path + os.sep + date + '_' + str(num) + '.' + image_url.split('.')[-1]
        with open(output_path, 'wb') as f:
            f.write(img_data)
        return output_path
    
    def divide_text_by_count(self, text):
        # divide content length english:280, unicode:140
        texts = []
        count = 0
        sub_text = ''
        for c in text:
            if unicodedata.east_asian_width(c) in 'FWA':
                count += 2
            else:
                count += 1
            if count > self.TWITTER_TEXT_LIMIT:
                texts.append(sub_text)
                count = 0
                sub_text = ''
            sub_text += c
        texts.append(sub_text)
        return texts

    def tweet_article(self, articles, work_dir):
        self.work_path = work_dir
        previous_tweet_id = None
        for article in articles:
            texts = self.divide_text_by_count(article.content)
            for tweet_idx, text in enumerate(texts):
                if tweet_idx == 0:  # 1st tweet for 1 article
                    if len(article.image_urls) == 0:  # no image
                        res = self.client.create_tweet(text = text)
                        previous_tweet_id = res.data['id']
                    else:  # with image
                        media_ids = []
                        for image_idx, url in enumerate(article.image_urls):
                            if image_idx <= 3:
                                image_path = self.fetch_image(url, article.date, image_idx)
                                media = self.api.media_upload(filename=image_path)
                                media_ids.append(media.media_id)
                        res = self.client.create_tweet(text=text, media_ids=media_ids)
                        previous_tweet_id = res.data['id']
                else:  # no image, with parent tweet id
                    res = self.client.create_tweet(text=text, in_reply_to_tweet_id=previous_tweet_id)
                    previous_tweet_id = res.data['id']
        return True
