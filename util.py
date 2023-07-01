#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import requests
import shutil
from datetime import datetime, timedelta
from dateutil.tz import gettz
from dateutil import parser

class Util:

    tz_str = 'Asia/Tokyo'
    
    def datetime_to_iso8601(self, dt): 
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    def date_to_iso_format(self, date):
        return datetime.fromisoformat(date).isoformat()
        
    def daterange_to_list(self, start, end):
        s = datetime.strptime(start, '%Y-%m-%d')
        e = datetime.strptime(end, '%Y-%m-%d')
        for n in range((e - s).days):
            yield (s + timedelta(n)).strftime('%Y-%m-%d')

    def local_date_to_utc_datetime(self, date):
        td = gettz(Util.tz_str).utcoffset(datetime.now())
        return datetime.fromisoformat(date) - td
    
    def utc_str_to_local(self, datetime_str):
        return parser.parse(datetime_str).astimezone(gettz(Util.tz_str))