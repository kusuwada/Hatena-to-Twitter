#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# refer: https://developer.hatena.ne.jp/ja/documents/blog/apis/atom/

import os
import re
import yaml
import requests
import hashlib
import random
import base64
import xml.etree.ElementTree as ET
from logging import getLogger, config
from datetime import datetime, timedelta, timezone
from util import Util
from article import Article

logger = getLogger(__name__)

class Hatena:

    media_url = 'https://f.hatena.ne.jp/atom/post'
    media_dir_name = 'Twitter Photos'
    default_category = ['twitter']
    hatena_image_pattern = r'\[f\:id\:kusuwada\:[a-z0-9]*\:plain\]'
    url_pattern = 'img src="(https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*))"'
    
    def __init__(self, user_id, blog_id):
        self.user_id = user_id
        self.root_endpoint = 'https://blog.hatena.ne.jp/' + user_id + '/' + blog_id + '/atom'
        self.wsse = None
    
    def auth(self):
        ut = Util()
        created = ut.datetime_to_iso8601(datetime.now())
        nonce = hashlib.sha1(str(random.random()).encode()).digest()
        digest = hashlib.sha1(nonce + created.encode() + os.environ['HT_KEY'].encode()).digest()
        s = 'UsernameToken Username="{0}", PasswordDigest="{1}", Nonce="{2}", Created="{3}"'
        self.wsse = s.format(self.user_id, base64.b64encode(digest).decode(), base64.b64encode(nonce).decode(), created)
        return

    def return_contents(self, entry):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text
        content = entry.find('{http://www.w3.org/2005/Atom}content').text
        formatted_content = entry.find('{http://www.hatena.ne.jp/info/xmlns#}formatted-content').text
        return title, content, formatted_content

    def select_elements_of_tag(self, xml_root, tag):
        return xml_root.findall(tag)

    def is_draft(self, entry):
        draft_status = (
            entry.find('{http://www.w3.org/2007/app}control')
            .find('{http://www.w3.org/2007/app}draft').text
        )
        return draft_status == 'yes'

    def return_published_date(self, entry):
        publish_date_str = entry.find('{http://www.w3.org/2005/Atom}published').text
        return datetime.fromisoformat(publish_date_str)

    def is_in_period(self, datetime_, start, end):
        return start <= datetime_ < end
    
    def convert_date_to_datetime(self, date, tz):
        year = int(date.split('-')[0])
        month = int(date.split('-')[1])
        day = int(date.split('-')[2])
        return datetime(year, month, day, tzinfo=tz)

    def fetch_images_from_content(self, content):
        result = re.findall(self.url_pattern, content)
        return result
    
    def is_image_in_content(self, content):
        pattern = re.compile(self.hatena_image_pattern)
        m = pattern.search(content)
        if m:
            return True
        else:
            return False
    
    def remove_image_from_content(self, content):
        pattern = re.compile(self.hatena_image_pattern)
        m = pattern.search(content)
        return re.sub(self.hatena_image_pattern, '', content)

    def fetch_my_article(self, date):
        try:
            tz = timezone(timedelta(seconds=9 * 60 * 60))
            start_datetime = self.convert_date_to_datetime(date, tz)
            end_datetime = start_datetime + timedelta(days=1)
            url = self.root_endpoint + '/entry'
            oldest_article_date = datetime.now(tz)
        except Exception as e:
            logger.error(e)
        
        target_entries = []
        articles = []
        logger.info('Start Fetcing Articles [' + str(start_datetime) + '] to [' + str(end_datetime) + ']')

        ##while start_datetime <= oldest_article_date:
        for i in range(1):
            res = requests.get(url, headers={'X-WSSE': self.wsse})
            root = ET.fromstring(res.text)

            links = self.select_elements_of_tag(root, '{http://www.w3.org/2005/Atom}link')
            #print(links)
            for link in links:
                #print(link.attrib)
                if 'next' == link.attrib['rel']:
                    print('good!')
                    print(link.attrib['href'])
            
            entries = self.select_elements_of_tag(root, '{http://www.w3.org/2005/Atom}entry')
            logger.info(f'links:{links}, entries: {len(entries)}')

            for entry in entries:
                if self.is_draft(entry):
                    continue
                article_date = self.return_published_date(entry)
                if oldest_article_date > article_date:
                    oldest_article_date = article_date
                    logger.info(f'[TEST2 LOG] oldest: {oldest_article_date} - start: {start_datetime} - current: {article_date}')
                if self.is_in_period(oldest_article_date, start_datetime, end_datetime):
                    target_entries.append(entry)
            logger.info(f'until {oldest_article_date} - articles: {len(target_entries)}')
        
        for entry in target_entries:
            article = Article()
            title, content, formatted_content = self.return_contents(entry)
            if self.is_image_in_content(content):
                content = self.remove_image_from_content(content).rstrip()
                article.image_urls = self.fetch_images_from_content(formatted_content)
            article.date = title
            article.content = content
            articles.append(article)

        return articles
