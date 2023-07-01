#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import yaml
from logging import config, getLogger, INFO
from hatena import Hatena
from twitter import Twitter
from article import Article

with open('log_config.yml', 'r') as f:
        log_config = yaml.safe_load(f.read())
        config.dictConfig(log_config)
logger = getLogger(__name__)

def main(date, ht_id, ht_host, work_dir, tz='Etc/UTC'):

    ## set timezone
	Util.tz_str = tz
	## set tmp media filepath
	media_path = work_dir

    logger.info('[START]' + date)

    ## fetch articles from hatena
    ht = Hatena(ht_id, ht_host)
    ht.auth()
    articles = ht.fetch_my_article(start, end)
    logger.info('Finish fetching target articles from Hatena. Number of articles: ' + str(len(articles)))
    for a in articles:
        logger.info(a)

    ## post to twitter
    tw = Twitter()
    tw.auth()
    tw.tweet_article(articles)

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='export hatena to twitter.')
	parser.add_argument('start', help='start date to export. [YYYY-MM-DD]')
	parser.add_argument('end', help='end date to export. [YYYY-MM-DD]')
	parser.add_argument('tw_id', help='Twitter name')
	parser.add_argument('ht_id', help='Hatena ID')
	parser.add_argument('ht_host', help='Hatena domain. e.g. example.hatenadiary.com')
	parser.add_argument('work_dir', help='working directory path')
	parser.add_argument('--tz', help='timezone')
	args = parser.parse_args()

    ut = Util()
	for date in ut.daterange_to_list(args.start, args.end):
		try:
			daily.daily(date, args.ht_id, args.ht_host, args.work_dir, args.tz)
		except RequestExceededError as e:
			logger.error(e)
			sys.exit(1)
		except Exception as e:
			logger.error(e)
