#!/usr/bin/env python3
# -*- coding:utf-8 -*-

class Article:

    def __init__(self):
        self.date = None
        self.content = None
        self.image_urls = []
    
    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)
