# -*- coding: utf-8 -*-
"""
Written by Jorgen 2020.04.22
This script:
    analyzes usage & "utilization" rates
"""

import os

# establish the Data Processing directory
abspath        = os.path.abspath(__file__)
folderfilepair = os.path.split(abspath)
folderpath     = folderfilepair[0]
dataprocpath   = os.path.realpath( \
                          os.path.join('..','Data Processing') )
procfilepath   = os.path.join(dataprocpath,'trawlHTML.py')

exec(open(procfilepath).read())


# %% first bit of sleuthing: which Pokemon is active most often?
# compute the fraction of player-turns during which a pokemon was active

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
        
        
        p1switch_dict = dict()
        p2switch_dict = dict()
        
        for p1enum in enumerate(p1switch_contents):
            textind  = p1enum[1][0]
            pokename = p1enum[1][1]
            
            if p1enum[0] < (len(p1switch_contents)-1):
                nextind         = p1switch_contents[p1enum[0]+1][0]
                turns_contained = [x[0]>textind and x[0]<nextind for x in turn_contents]
                
                # leverage the ability to sum logical lists
                number_turns_contained = sum(turns_contained)
                
            else:
                turns_contained = [x[0]>textind for x in turn_contents]
                number_turns_contained = sum(turns_contained)
                
            
            if pokename in p1switch_dict:
                p1switch_dict[pokename] = p1switch_dict[pokename] + number_turns_contained
            else:
                p1switch_dict[pokename] = number_turns_contained
                
                
        for p2enum in enumerate(p2switch_contents):
            textind  = p2enum[1][0]
            pokename = p2enum[1][1]
            
            if p2enum[0] < (len(p2switch_contents)-1):
                nextind         = p2switch_contents[p2enum[0]+1][0]
                turns_contained = [x[0]>textind and x[0]<nextind for x in turn_contents]
                
                # leverage the ability to sum logical lists
                number_turns_contained = sum(turns_contained)
                
            else:
                turns_contained = [x[0]>textind for x in turn_contents]
                number_turns_contained = sum(turns_contained)
                
            
            if pokename in p2switch_dict:
                p2switch_dict[pokename] = p2switch_dict[pokename] + number_turns_contained
            else:
                p2switch_dict[pokename] = number_turns_contained
                
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
        
        p1dict = p1switch_dict
        p2dict = p2switch_dict
        
        # add a field that counts total turns
        turncount_p1 = 0
        for key in p1dict:
            turncount_p1 = turncount_p1 + p1dict[key]
            
        turncount_p2 = 0
        for key in p2dict:
            turncount_p2 = turncount_p2 + p2dict[key]
            
        p1dict['turncount'] = turncount_p1
        p2dict['turncount'] = turncount_p2
        
        p1dict['win'] = p1_winner
        p2dict['win'] = p2_winner
        
        if p1_winner:
            winnerlist.append(p1dict)
            loserlist.append(p2dict)
        elif p2_winner:
            winnerlist.append(p2dict)
            loserlist.append(p1dict)
        else:
            tielist.append(p1dict)
            tielist.append(p2dict)

# %% winner & loser fractions. ignore the seven ties for now
winner_fractions = dict()
loser_fractions  = dict()

totalgames       = 0

for winfo in enumerate(winnerlist):
    # game must last at least 20 turns
    tc = winfo[1]['turncount']
    
    if tc >= 20:
        pokenames = list(winfo[1])
        pokenames = pokenames[:-2]
        totalgames = totalgames + 1
        
        for pname in enumerate(pokenames):
            current_frac = winfo[1][pname[1]] / winfo[1]['turncount']
            
            if pname[1] not in winner_fractions:
                winner_fractions[pname[1]] = list()
                winner_fractions[pname[1]].append(current_frac)
            else:
                winner_fractions[pname[1]].append(current_frac)


for linfo in enumerate(loserlist):
    # game must last at least 20 turns
    tc = linfo[1]['turncount']
    
    if tc >= 20:
        pokenames = list(linfo[1])
        pokenames = pokenames[:-2]
        
        for pname in enumerate(pokenames):
            current_frac = linfo[1][pname[1]] / linfo[1]['turncount']
            
            if pname[1] not in loser_fractions:
                loser_fractions[pname[1]] = list()
                loser_fractions[pname[1]].append(current_frac)
            else:
                loser_fractions[pname[1]].append(current_frac)
                
winner_usages = dict()
loser_usages  = dict()

for winfo in enumerate(winner_fractions):
    winner_usages[winfo[1]] = len(winner_fractions[winfo[1]])
    
winner_usages_sorted = sorted(winner_usages.items(), key=lambda item: item[1], reverse = True)

for linfo in enumerate(loser_fractions):
    loser_usages[linfo[1]] = len(loser_fractions[linfo[1]])
    
loser_usages_sorted = sorted(loser_usages.items(), key=lambda item: item[1], reverse = True)

# %% correlation of winner vs loser usages

import matplotlib.pyplot as plt

x_usages = []
y_usages = []
winrates = dict()

for winfo in enumerate(winner_usages):
    wusage = winner_usages[winfo[1]]
    
    if wusage >= 5:
        lusage = loser_usages[winfo[1]]
        x_usages.append(wusage)
        y_usages.append(lusage)
        winrates[winfo[1]] = wusage/(wusage + lusage)
        
    else:
        pass
    
winrates_sorted = sorted(winrates.items(), key=lambda item: item[1], reverse = True)

wr = list()
tu = list()
for x in enumerate(x_usages):
    wr_temp = x_usages[x[0]] / ( x_usages[x[0]] + y_usages[x[0]] )
    wr.append(wr_temp)
    tu.append(x_usages[x[0]] + y_usages[x[0]])
    

    
plt.figure()
plt.scatter(x_usages,y_usages)

plt.xlim((0,300))
plt.ylim((0,300))

plt.plot([0,300],[0,300],'k-')
plt.xlabel('winning team uses')
plt.ylabel('losing team uses')



plt.figure()
plt.scatter(tu,wr)

plt.ylim((0,1))
plt.xlim((0,600))
plt.xlabel('number of uses')
plt.ylabel('win rate')

# %%
import numpy as np

# assumption of 50% true win rate
# compute the expected standard error
xvals = np.arange(10,600,10)
yvals = 2*np.sqrt(0.5**2 / xvals)

plt.plot(xvals,0.5+yvals,'k-')
plt.plot(xvals,0.5-yvals,'k-')

# %% now to look at "utilization rate"

pnames   = list()
winmu    = list()
winse    = list()
losemu   = list()
losese   = list()
totalusage = list()
winusage = list()
loseusage = list()

for winfo in enumerate(winner_fractions):
    pname = winfo[1]
    
    if pname in loser_fractions:
        wvals = winner_fractions[pname]
        lvals = loser_fractions[pname]
        
        lw = len(wvals)
        ll = len(lvals)
        lt = lw + ll
        
        if lt >= 15 and lw >= 5 and ll >= 5: # at least 15 battles total, with at least 5 wins and 5 losses
            pnames.append(pname)
            winmu.append(np.mean(wvals))
            losemu.append(np.mean(lvals))
            winse.append(np.std(wvals) / np.sqrt(lw))
            losese.append(np.std(lvals) / np.sqrt(ll))
            totalusage.append(lt)
            winusage.append(lw)
            loseusage.append(ll)
        else:
            pass
    else:
        pass

rat = list()
for ind in enumerate(winmu):
    rat.append( np.log2(winmu[ind[0]] / losemu[ind[0]]) )
    
wrat = list()
for ind in enumerate(winusage):
    wrat.append( winusage[ind[0]] / (winusage[ind[0]] + loseusage[ind[0]]) )

plt.figure()
plt.scatter(winmu,losemu)
plt.xlim((0,0.3))
plt.ylim((0,0.3))

plt.plot([0,0.3],[0,0.3],'k-')
plt.xlabel('winning team utilization rate')
plt.ylabel('losing team utilization rate')

plt.figure()
plt.scatter(totalusage,rat)
plt.xlim((0,600))
plt.xlabel('total usage')
plt.ylabel('log utilization ratio, win:lose')

plt.figure()
plt.scatter(wrat,rat)
plt.xlim((0,1))
plt.xlabel('win rate, usage')
plt.ylabel('log utilization ratio, win:lose')

# so utilization rate indeed does not correlate with win rate per se, BUT it scales with uncertainty and nothing else. i.e., it's still a pretty useless metric whose only fluctuations seem to be random chance
