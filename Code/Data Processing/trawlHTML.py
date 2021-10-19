# -*- coding: utf-8 -*-
"""
Written by Jorgen 2020.01.21
This script:
    Trawls through all the subdirectories of "Data"
    Loads in each HTML file
    Parses battle information from them
"""

# import necessary packages
from bs4 import BeautifulSoup
import os
import re

# establish the Data directory
abspath        = os.path.abspath(__file__)
folderfilepair = os.path.split(abspath)
folderpath     = folderfilepair[0]
datapath       = os.path.realpath( \
                          os.path.join('..','..','Data') )

# create list of file paths for matches
list_of_htmls = list()
for root, dirs, files in os.walk(datapath):
    for name in files:
        if name.endswith('.html'):
            list_of_htmls.append(os.path.join(root,name))
           
"""
do I wanna preserve time information to track trends as they evolved between 2016 - 2019? Ehhh yeah tbh.
I mean, I wanna do year-to-year (or tourney-to-tourney) reliability stats on my metrics
In addition to excluding this year's SPL stats to date so I can talk during midseason about whether my metrics track with who's doing the best so far in SPL
BUT do I need to create those metadata NOW or can I parse file paths AFTER the fact?
...let's do the latter
"""

# %% GET ALL TAG NAMES ACROSS ALL FILES
set_of_tags   = set()
list_of_tags  = list()
list_of_files = list()

for fel in enumerate(list_of_htmls):
    try:
        with open(fel[1],encoding='utf-8') as htmlfile: # make utf-8 encoding explicit so that emojis can be handled
            soup    = BeautifulSoup(htmlfile.read(),"html.parser")
            #            soup    = BeautifulSoup(htmlfile.read(),"lxml") # supposedly a more robust parser

            battlog = soup.find("script",attrs={"class": "battle-log-data"})
            btext   = battlog.get_text()
            
            # trawl for the first thing between the first || in each line
            fmobj           = re.search('\|[^\|\n]+\|', btext)
            firstmatch_     = [fmobj.group(0)]
            firstinds_      = [(fmobj.start(0),fmobj.end(0))]
            
            subseqmatch_    = re.findall('\n\|[^\|\n]+\|',btext)
            subseqinds_     = [(m.start(0), m.end(0)) for m in re.finditer('\n\|[^\|\n]+\|', btext)]
            
            for el in enumerate(subseqmatch_):
                subseqmatch_[el[0]] = el[1][1:] # delete leading \n
                
            allmatch_       = firstmatch_ + subseqmatch_
            allinds_        = firstinds_ + subseqinds_
            
            for el in enumerate(allmatch_):
                oldlen = len(set_of_tags)
                set_of_tags.add(el[1])
                newlen = len(set_of_tags)
                
                if newlen > oldlen:
                    list_of_tags.append(el[1])
                    list_of_files.append(fel[1])
                
    except:
        print("oops! "+fel[1]+" is a bad file!")
    
    #    newline_locs  = [(m.start(0), m.end(0)) for m in re.finditer('\n', btext)]
    #    firstline_loc = [(-1,0)]
    #    newline_locs  = firstline_loc + newline_locs
    #    vertsep_locs  = [(m.start(0), m.end(0)) for m in re.finditer('\|', btext)]
    
# %% now go thru each tag & pull the text associated with each. use a dict to keep track of it all

event_dict = dict()
match_dict = dict()

for thistag in enumerate(list_of_tags):
    event_dict[thistag[1]] = list()
    match_dict[thistag[1]] = list()
    
for fel in enumerate(list_of_htmls):
    with open(fel[1],encoding='utf-8') as htmlfile: # make utf-8 encoding explicit so that emojis can be handled
        soup    = BeautifulSoup(htmlfile.read(),"html.parser")
        #            soup    = BeautifulSoup(htmlfile.read(),"lxml") # supposedly a more robust parser

        battlog = soup.find("script",attrs={"class": "battle-log-data"})
        btext   = battlog.get_text()
            
        # trawl for the first thing between the first || in each line
        fmobj           = re.search('\|[^\|\n]+\|', btext)
        firstmatch_     = [fmobj.group(0)]
        firstinds_      = [(fmobj.start(0),fmobj.end(0))]
            
        subseqmatch_    = re.findall('\n\|[^\|\n]+\|',btext)
        subseqinds_     = [(m.start(0), m.end(0)) for m in re.finditer('\n\|[^\|\n]+\|', btext)]
            
        for el in enumerate(subseqmatch_):
            subseqmatch_[el[0]] = el[1][1:] # delete leading \n
                
        allmatch_       = firstmatch_ + subseqmatch_
        allinds_        = firstinds_ + subseqinds_
            
        # for each tag
        for taginds in enumerate(allinds_):
            tagstr      = allmatch_[taginds[0]]
            btext_following_tag = btext[(taginds[1][1]):] # python excludes the last value when indexing
            # so each element of taginds marks the first index where there is NOTHING remaining of the tag!
            # in other words, no +1 nonsense required!
                
            # find the first newline following the tag
            last_thistag_ind = re.search('\n',btext_following_tag)
            
            if last_thistag_ind is None:
                tagcontents = btext_following_tag
            else:
                # remember, python excludes the last index in these operations
                # so you don't gotta do a minus-one thing here!
                tagcontents = btext_following_tag[:(last_thistag_ind.start(0))]
            
            # append to the list in event_dict
            event_dict[tagstr].append(tagcontents)
            match_dict[tagstr].append(fel[0])