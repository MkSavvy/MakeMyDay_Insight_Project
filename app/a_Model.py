# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 11:52:02 2015

@author: Michel_home
"""
import re

def urlExtract(url_string = ""):
  pat = re.compile("\/id\/([\w-]+)\/")
  url = re.findall(pat, url_string)
  if url:
      return url[0]
  else:
      return ""

