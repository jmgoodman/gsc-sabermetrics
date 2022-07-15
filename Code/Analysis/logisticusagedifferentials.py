# -*- coding: utf-8 -*-
"""
Written by Jorgen 2020.05.10
This script:
    looks at the "usage differential" of each pokemon in each match,
    then builds a logistic regression model to see how well one can predict the result of a match
    knowing only the Pokemon that are going into it
"""

from bs4 import BeautifulSoup
import os
import re
import numpy as np
import matplotlib.pyplot as plt
import random as rand
from sklearn import linear_model as lm

# establish the Data Processing directory
abspath        = os.path.abspath(__file__)
folderfilepair = os.path.split(abspath)
folderpath     = folderfilepair[0]
dataprocpath   = os.path.realpath( \
                          os.path.join('..','Data Processing') )
procfilepath   = os.path.join(dataprocpath,'trawlHTML.py') 

exec(open(procfilepath).read())
# list_of_htmls is created by this script, ignore code analyzer warnings

# %% extract the usage differentials

# first, you need to get the teams!
winnerlist = list()
loserlist  = list()
tielist    = list()

for fel in enumerate(list_of_htmls):
    with open(fel[1],encoding='utf-8') as htmlfile: # make utf-8 encoding explicit so that emojis can be handled
        soup    = BeautifulSoup(htmlfile.read(),"html.parser")
        #            soup    = BeautifulSoup(htmlfile.read(),"lxml") # supposedly a more robust parser

        battlog = soup.find("script",attrs={"class": "battle-log-data"})
        btext   = battlog.get_text()
        
        # seek all instances of switches or turns
        p1switch_re = '\|switch\|p1a\:[^\|]+\|'
        p2switch_re = '\|switch\|p2a\:[^\|]+\|'
        turn_re     = '\|turn\|'
        
        p1switch_inds = [(m.start(0), m.end(0)) for m in re.finditer(p1switch_re, btext)]
        p2switch_inds = [(m.start(0), m.end(0)) for m in re.finditer(p2switch_re, btext)]
        turn_inds     = [(m.start(0), m.end(0)) for m in re.finditer(turn_re, btext)]
        
        p1switch_contents = list()
        p2switch_contents = list()
        turn_contents     = list()
        
        for p1enum in enumerate(p1switch_inds):
            startind   = p1enum[1][1]
            btext_     = btext[startind:]
            seekobj    = re.search('(\||,)',btext_)
            firstinds_ = [(seekobj.start(0),seekobj.end(0))]
            switchmon  = btext_[:firstinds_[0][0]]
            p1switch_contents.append((startind,switchmon))
        
        for p2enum in enumerate(p2switch_inds):
            startind   = p2enum[1][1]
            btext_     = btext[startind:]
            seekobj    = re.search('(\||,)',btext_)
            firstinds_ = [(seekobj.start(0),seekobj.end(0))]
            switchmon  = btext_[:firstinds_[0][0]]
            p2switch_contents.append((startind,switchmon))
            
        for turnenum in enumerate(turn_inds):
            startind   = turnenum[1][1]
            btext_     = btext[startind:]
            seekobj    = re.search('\n',btext_)
            firstinds_ = [(seekobj.start(0),seekobj.end(0))]
            turnind    = btext_[:firstinds_[0][0]]
            turn_contents.append((startind,int(turnind)))
        
        p1switch_list = list()
        p2switch_list = list()
        
        for p1enum in enumerate(p1switch_contents):
            pokename = p1enum[1][1]
            
            if pokename in p1switch_list:
                pass
            else:
                p1switch_list.append(pokename)
                
                
        for p2enum in enumerate(p2switch_contents):
            pokename = p2enum[1][1]
            
            if pokename in p2switch_list:
                pass
            else:
                p2switch_list.append(pokename)
                
        # only use matches where all 6 pokes on each side are known
        if len(p1switch_list) == 6 and len(p2switch_list) == 6:
        
            # figure out win & loss metadata
            p1_marker_re = '\|player\|p1\|'
            p2_marker_re = '\|player\|p2\|'
            
            seekobj_p1   = re.search(p1_marker_re,btext)
            seekobj_p2   = re.search(p2_marker_re,btext)
            
            indp1 = seekobj_p1.end(0)
            indp2 = seekobj_p2.end(0)
            
            btext_p1 = btext[indp1:]
            btext_p2 = btext[indp2:]
            
            seekname_p1 = re.search('[^\|]+\|',btext_p1)
            seekname_p2 = re.search('[^\|]+\|',btext_p2)
            
            nameind_p1  = seekname_p1.end(0)
            nameind_p2  = seekname_p2.end(0)
            
            namestr_p1  = btext_p1[:(nameind_p1-1)]
            namestr_p2  = btext_p2[:(nameind_p2-1)]
            
            winner_marker_re = '\|win\|'
            seekobj_win      = re.search(winner_marker_re,btext)
            
            if seekobj_win is not None:
                indwin           = seekobj_win.end(0)
                btext_win        = btext[indwin:]
                seekname_win     = re.search('[^(\||\n)]+(\||\n)',btext_win)
                
                if seekname_win is not None:
                    nameind_win      = seekname_win.end(0)
                    namestr_win      = btext_win[:(nameind_win-1)]
                else:
                    namestr_win      = btext_win
                
                p1_winner = namestr_win == namestr_p1
                p2_winner = namestr_win == namestr_p2
            else:
                p1_winner = False
                p2_winner = False
            
            if p1_winner:
                winnerlist.append(p1switch_list)
                loserlist.append(p2switch_list)
            elif p2_winner:
                winnerlist.append(p2switch_list)
                loserlist.append(p1switch_list)
            else:
                tielist.append(p1switch_list)
                tielist.append(p2switch_list)
        else:
            pass

# next, you need to collect "usage differentials" of each pokemon
# which means first identifying which pokemon were even used
totalpokesused = list()

for ind in range(len(winnerlist)):
    totalpokesused = totalpokesused + winnerlist[ind] + loserlist[ind]
    
uniquepokesused = set(totalpokesused)
uniquepokeslist = list(uniquepokesused)

usage_differential_mat = np.zeros((len(winnerlist),len(uniquepokeslist)))

for gameind in range(len(winnerlist)):
    winnerpokes = winnerlist[gameind]
    loserpokes  = loserlist[gameind]
    for pokeind in range(len(uniquepokeslist)):
        thispoke = uniquepokeslist[pokeind]
        
        winnerhas = thispoke in winnerpokes
        loserhas  = thispoke in loserpokes
        
        # thank god for automatic re-casting of logical as integer
        usediff = winnerhas - loserhas
        
        usage_differential_mat[gameind,pokeind] = usediff

# create a winner-loser predictor that is only HALF populated by winners (choose losers at random)
WLlist = np.zeros(len(winnerlist))
winnerinds = np.arange(0,len(WLlist),2) # do every other index so your cross-validation doesn't end up biased toward one "class" (winner or loser) over the other

for ind in range(len(winnerinds)):
    wind = winnerinds[ind]
    WLlist[wind] = 1
    
# multiply rows associated with LOSERS by negative 1
usage_differential_mat_ = usage_differential_mat.copy() # to verify that the correct rows were indeed "flipped" from the "everybody's a winner" case
for ind in range(len(WLlist)):
    islose = WLlist[ind] == 0
    
    if islose:
        # negate the row to reflect the loser's perspective
        usage_differential_mat[ind,:] = -usage_differential_mat[ind,:]

# %% book-keeping: split into training, validation, and test sets
testinds  = np.arange(0,len(WLlist),5)
validinds = np.arange(1,len(WLlist),5)
traininds = [x for x in range(len(WLlist)) if x not in testinds and x not in validinds]

WLtrain   = WLlist[traininds]
usdtrain  = usage_differential_mat[traininds,:]

WLvalid   = WLlist[validinds]
usdvalid  = usage_differential_mat[validinds,:]

WLtest    = WLlist[testinds]
usdtest   = usage_differential_mat[testinds,:]

# only use columns with entries across all 3 of training, validation, and test sets
keepcols = list()

for ind in range(len(uniquepokeslist)):
    traincol = usdtrain[:,ind]
    validcol = usdvalid[:,ind]
    testcol  = usdtest[:,ind]
    
    # seek dudes with at least 5 instances in valid / test, and 15 in train
    traininstances = np.sum(np.abs(traincol))
    validinstances = np.sum(np.abs(validcol))
    testinstances  = np.sum(np.abs(testcol))
    
    if traininstances < 15 or validinstances < 5 or testinstances < 5:
        keepcols.append(False)
    else:
        keepcols.append(True)

usdtrain  = usdtrain[:,keepcols]
usdvalid  = usdvalid[:,keepcols]
usdtest   = usdtest[:,keepcols]
pokenames = [uniquepokeslist[ind] for ind in range(len(uniquepokeslist)) if keepcols[ind]]
# %% model selection: step-wise glm

Cvals = np.logspace(-5,5,100)
fitvals = np.zeros(np.shape(Cvals))
pR2vals = np.zeros(np.shape(Cvals))
fitvals_train = np.zeros(np.shape(Cvals))
for cind in range(len(Cvals)):
    cval = Cvals[cind]
    trainmdl = lm.LogisticRegression(penalty='l1',fit_intercept=True,solver='liblinear',max_iter=1000,C=cval)
    trainmdl.fit(usdtrain,WLtrain)
    fitvals[cind] = trainmdl.score(usdvalid,WLvalid) # these never crack 50% (i.e., literal CHANCE level). That's... real bad. Is this a problem with regularization, or are the data actually this poor a predictor of victory?
    fitvals_train[cind] = trainmdl.score(usdtrain,WLtrain)
    
    probvals = trainmdl.predict_proba(usdvalid)
    pv       = probvals[:,1] # probabilities of winning
    
    dev_vals = np.zeros(len(WLvalid))
    
    for WLind in range(len(WLvalid)):
        predix_ = pv[WLind]
        WLval   = WLvalid[WLind]
        
        if WLval == 1:
            dev_vals[WLind] = np.log(predix_)
        else:
            dev_vals[WLind] = np.log(1-predix_) # probability of a loss happening given that... y'know... it did
            
    dev_total = np.sum(dev_vals)
    
    dev_null  = np.log(0.5) * len(WLvalid) # by design, we have 50% wins and 50% losses here. The null model will be 50%
    
    # def_full is necessarily 0. if a loss is perfectly called, p = 0, and 1-p = 1. If a win is perfectly called, p = 1. log(1) is 0, and a sum of 0s is 0.
    
    pR2 = 1 - (dev_total/dev_null)
    pR2vals[cind] = pR2

# ...yeah. these models are just real bad at predicting who will win & who will lose