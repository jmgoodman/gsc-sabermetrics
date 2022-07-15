# -*- coding: utf-8 -*-
"""
Written by Jorgen 2020.05.09
This script:
    analyzes lead usage, matchups, and their tendency to win/lose matches
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import random as rand

# establish the Data Processing directory
abspath        = os.path.abspath(__file__)
folderfilepair = os.path.split(abspath)
folderpath     = folderfilepair[0]
dataprocpath   = os.path.realpath( \
                          os.path.join('..','Data Processing') )
procfilepath   = os.path.join(dataprocpath,'trawlHTML.py')

exec(open(procfilepath).read())

# %%
winner_leads = list()
loser_leads  = list()

# elements of winner & loser leads correspond with one another
for fel in enumerate(list_of_htmls):
    with open(fel[1],encoding='utf-8') as htmlfile: # make utf-8 encoding explicit so that emojis can be handled
        soup    = BeautifulSoup(htmlfile.read(),"html.parser")
        #            soup    = BeautifulSoup(htmlfile.read(),"lxml") # supposedly a more robust parser

        battlog = soup.find("script",attrs={"class": "battle-log-data"})
        btext   = battlog.get_text()
        
        # seek the lead pokemon in each match (i.e. the first instance of a "switch" event)
        p1_lead_re = '\|switch\|p1a:[^\|]+\|[^\|]+\|'
        p2_lead_re = '\|switch\|p2a:[^\|]+\|[^\|]+\|'
        
        p1_lead_obj     = re.search(p1_lead_re, btext)
        p2_lead_obj     = re.search(p2_lead_re, btext)
        
        p1_lead_inds    = (p1_lead_obj.start(0),p1_lead_obj.end(0))
        p2_lead_inds    = (p2_lead_obj.start(0),p2_lead_obj.end(0))
        
        p1_lead_text    = btext[p1_lead_inds[0]:p1_lead_inds[1]]
        p2_lead_text    = btext[p2_lead_inds[0]:p2_lead_inds[1]]
        
        p1_find_comma   = re.search(',',p1_lead_text)
        p2_find_comma   = re.search(',',p2_lead_text)
        
        p1_priortoname  = re.search('\|switch\|p1a:[^\|]+\|',p1_lead_text)
        p2_priortoname  = re.search('\|switch\|p2a:[^\|]+\|',p2_lead_text)
        
        if p1_find_comma is None:
            p1_lead_name = p1_lead_text[p1_priortoname.end(0):-1]
        else:
            p1_lead_name = p1_lead_text[p1_priortoname.end(0):(p1_find_comma.start(0))]
            
        if p2_find_comma is None:
            p2_lead_name = p2_lead_text[p2_priortoname.end(0):-1]
        else:
            p2_lead_name = p2_lead_text[p2_priortoname.end(0):(p2_find_comma.start(0))]
        
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
            is_winner = True
        else:
            p1_winner = False
            p2_winner = False
            is_winner = False # there are a total of 7 tied matches in this dataset. That simply is not very many, and it's hard to draw any solid conclusions from such a small sample - though I will say that these matches disproportionately use Blissey!
            
        if is_winner:
            if p1_winner:
                winner_leads.append(p1_lead_name)
                loser_leads.append(p2_lead_name)
            elif p2_winner:
                winner_leads.append(p2_lead_name)
                loser_leads.append(p1_lead_name)
                
unique_lead_set  = set(winner_leads+loser_leads)
unique_lead_list = list(unique_lead_set)

combinedleads    = winner_leads + loser_leads

unique_lead_usage_counts = list()

for currentlead in enumerate(unique_lead_list):
    is_this_lead = [leadname[1] == currentlead[1] for leadname in enumerate(combinedleads)]
    n_uses       = sum(is_this_lead)
    unique_lead_usage_counts.append(n_uses)
    
# sort leads by usage
sorted_inds   = sorted(range(len(unique_lead_usage_counts)), key=lambda k: unique_lead_usage_counts[k],reverse=True)
sorted_usages = [unique_lead_usage_counts[sorted_ind] for sorted_ind in sorted_inds]
sorted_names  = [unique_lead_list[sorted_ind] for sorted_ind in sorted_inds]

# exclude any leads used fewer than 5 times
keep_inds    = [sorted_usage[0] for sorted_usage in enumerate(sorted_usages) if sorted_usage[1]>=5]

sorted_usages_supra = [sorted_usages[k] for k in keep_inds]
sorted_names_supra  = [sorted_names[k] for k in keep_inds]

winner_counts = list()
loser_counts  = list()

for sname in sorted_names_supra:
    wuse = [wlead == sname for wlead in winner_leads]
    luse = [llead == sname for llead in loser_leads]
    
    winner_counts.append(sum(wuse))
    loser_counts.append(sum(luse))
    
winrate_of_leads = [winner_counts[ind]/(sorted_usages_supra[ind]) for ind in range(len(sorted_names_supra))]

sem_of_winrates  = [ np.sqrt( (winrate_of_leads[ind] * (1-winrate_of_leads[ind])) /sorted_usages_supra[ind] ) for ind in range(len(sorted_names_supra)) ]

zscore_winrates  = [ (winrate_of_leads[ind]-0.5) / sem_of_winrates[ind] for ind in range(len(sorted_names_supra)) ]

# now make a big matrix
wincount_matrix = np.zeros((len(sorted_names_supra),len(sorted_names_supra)))

# make rows (first index) be winner and columns (second index) be loser
for ind in range(len(winner_leads)):
    winlead  = winner_leads[ind]
    loselead = loser_leads[ind]
    winind   = [x for x in range(len(sorted_names_supra)) if sorted_names_supra[x] == winlead]
    loseind  = [x for x in range(len(sorted_names_supra)) if sorted_names_supra[x] == loselead]
    
    if len(winind) == 1 and len(loseind) == 1:
        wincount_matrix[winind[0],loseind[0]] = wincount_matrix[winind,loseind]+1
        
totalmatch_mat = wincount_matrix + np.transpose(wincount_matrix)
winrate_mat    = np.divide(wincount_matrix, totalmatch_mat)

# yep, as expected... all winrate modulations are quite modest
# none of them rise above even the most liberal thresholds of statistical significance (the ones that don't bother to correct for multiple comparisons)
# turns out, trying to attribute wins & losses to just one factor such as this is a very silly endeavor!
# probably want to build a multivariate logistic regression model... and report statistically significant predictors of THAT, which accounts for the confounding factors of other variables!