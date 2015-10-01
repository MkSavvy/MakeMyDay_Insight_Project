# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 11:52:02 2015

@author: Michel_home
"""
import re
import pickle as pkl


def urlExtract(url_string = ""):
  pat = re.compile("\/id\/([\w-]+)\/")
  url = re.findall(pat, url_string)
  if url:
      return url[0]
  else:
      return "Error 404: Page not found! The url provided is not of proper format"


def getSimProjects(chosen):
    if 'bmatch' not in locals():
        with open("../Data/matchlist.pickle", 'rb') as f:
            bmatch = pkl.load(f)
    return bmatch.iloc[chosen]