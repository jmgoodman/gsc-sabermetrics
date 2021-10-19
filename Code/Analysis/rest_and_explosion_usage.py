# -*- coding: utf-8 -*-
"""
Written by Jorgen 2020.04.23
This script:
    analyzes rest & explosion usage and their correlations with victory
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

# %% explosion & rest usages (and win/loss statistics)

explosion_usage  = list()
rest_usage       = list()
st_usage         = list() # add sleep talk to offset the usage of rest
winnerplayerlist = list()

# we're going to count the number of uses of each of these moves
# we'll end up with a list of 2ples, with 2ple[0] being the winner usage and 2ple[1] being the loser usage
# |move|p1a: Raikou|Rest|
# |move|p2a: Steelix|Explosion|p1a: Raikou
for fel in enumerate(list_of_htmls):
    with open(fel[1],encoding='utf-8') as htmlfile: # make utf-8 encoding explicit so that emojis can be handled
        soup    = BeautifulSoup(htmlfile.read(),"html.parser")
        #            soup    = BeautifulSoup(htmlfile.read(),"lxml") # supposedly a more robust parser

        battlog = soup.find("script",attrs={"class": "battle-log-data"})
        btext   = battlog.get_text()
        
        # seek all instances of each player's move usage
        p1boom_re = '\|move\|p1a:[^\|]+\|(Explosion|Self-Destruct)\|'
        p2boom_re = '\|move\|p2a:[^\|]+\|(Explosion|Self-Destruct)\|'
        
        p1rest_re = '\|move\|p1a:[^\|]+\|Rest\|'
        p2rest_re = '\|move\|p2a:[^\|]+\|Rest\|'
        
        p1st_re   = '\|move\|p1a:[^\|]+\|Sleep Talk\|'
        p2st_re   = '\|move\|p2a:[^\|]+\|Sleep Talk\|'
        
        p1boom_inds = [(m.start(0), m.end(0)) for m in re.finditer(p1boom_re, btext)]
        p2boom_inds = [(m.start(0), m.end(0)) for m in re.finditer(p2boom_re, btext)]
        
        p1rest_inds = [(m.start(0), m.end(0)) for m in re.finditer(p1rest_re, btext)]
        p2rest_inds = [(m.start(0), m.end(0)) for m in re.finditer(p2rest_re, btext)]
        
        p1st_inds   = [(m.start(0), m.end(0)) for m in re.finditer(p1st_re, btext)]
        p2st_inds   = [(m.start(0), m.end(0)) for m in re.finditer(p2st_re, btext)]
        
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
            winnerplayerlist.append(0)
            
        if is_winner:
            if p1_winner:
                boom_tuple = (len(p1boom_inds),len(p2boom_inds))
                rest_tuple = (len(p1rest_inds),len(p2rest_inds))
                st_tuple   = (len(p1st_inds),len(p2st_inds))
                winnerplayerlist.append(1)
                
            elif p2_winner:
                boom_tuple = (len(p2boom_inds),len(p1boom_inds))
                rest_tuple = (len(p2rest_inds),len(p1rest_inds))
                st_tuple   = (len(p2st_inds),len(p1st_inds))
                winnerplayerlist.append(2)
                
            explosion_usage.append(boom_tuple)
            rest_usage.append(rest_tuple)
            st_usage.append(st_tuple)
                    

# %% boom & rest stats
#winnerboom = [x[0] for x in explosion_usage]
#loserboom  = [x[1] for x in explosion_usage]
#deltaboom  = [x-y for x,y in zip(winnerboom,loserboom)]
#
#winnerrest = [x[0] for x in rest_usage]
#loserrest  = [x[1] for x in rest_usage]
#deltarest  = [x-y for x,y in zip(winnerrest,loserrest)]
#
#winnerboom_jitter = [x-0.1+0.2*rand.random() for x in winnerboom]
#loserboom_jitter  = [x-0.1+0.2*rand.random() for x in loserboom]
#
#winnerrest_jitter = [x-0.1+0.2*rand.random() for x in winnerrest]
#loserrest_jitter  = [x-0.1+0.2*rand.random() for x in loserrest]


# %% explosion plots
#plt.figure()
#plt.scatter(winnerboom_jitter,loserboom_jitter,alpha=0.2)
#plt.xlabel('Explosion uses by winner')
#plt.ylabel('Explosion uses by loser')
#
#plt.figure()
#plt.hist(deltaboom,np.arange(-6.5,6.5))
#plt.xlabel('Explosion use difference, winner - loser')
#
#plt.figure()
#plt.hist(winnerboom,np.arange(-0.5,6.5))
#plt.xlabel('Explosion uses, winner')

# %% rest plots
#plt.figure()
#plt.scatter(winnerrest_jitter,loserrest_jitter,alpha=0.2)
#plt.xlabel('Rest uses by winner')
#plt.ylabel('Rest uses by loser')
#
#plt.figure()
#plt.hist(deltarest,np.arange(-30.5,30.5))
#plt.xlabel('Rest use difference, winner - loser')
#
#plt.figure()
#plt.hist(winnerrest,np.arange(-0.5,47.5))
#plt.xlabel('Rest uses, winner')

# %% okay let's focus on another event: first (net) blood

#firstbloodplayerlist = list()
#
#for fel in enumerate(list_of_htmls):
#    with open(fel[1],encoding='utf-8') as htmlfile: # make utf-8 encoding explicit so that emojis can be handled
#        soup    = BeautifulSoup(htmlfile.read(),"html.parser")
#        #            soup    = BeautifulSoup(htmlfile.read(),"lxml") # supposedly a more robust parser
#
#        battlog = soup.find("script",attrs={"class": "battle-log-data"})
#        btext   = battlog.get_text()
#        
#        p1faint_re = '\|faint\|p1a:[^(\||\n)]+\n'
#        p2faint_re = '\|faint\|p2a:[^(\||\n)]+\n'
#        
#        p1faint_inds     = [(m.start(0), m.end(0)) for m in re.finditer(p1faint_re, btext)]
#        p2faint_inds     = [(m.start(0), m.end(0)) for m in re.finditer(p2faint_re, btext)]
#        
#        l1 = len(p1faint_inds)
#        l2 = len(p2faint_inds)
#        
#        if l1 == 0 and l2 > 0:
#            firstbloodplayerlist.append(1) # remember: these are players with the first pokemon to FAINT, not the first one to score the kill!
#        elif l1 > 0 and l2 == 0:
#            firstbloodplayerlist.append(2)
#        elif l1 == 0 and l2 == 0:
#            firstbloodplayerlist.append(0)
#        else:
#            isdecision = False
#            
#            p1fi = p1faint_inds
#            p2fi = p2faint_inds
#            
#            while not isdecision:
#                p1f = p1fi[0]
#                p2f = p2fi[0]
#                
#                if p1f[0] == p2f[1] or p2f[0] == p1f[1]:
#                    p1fi = p1fi[1:]
#                    p2fi = p2fi[1:]
#                    
#                    l1 = len(p1fi)
#                    l2 = len(p2fi)
#                    
#                    if l1 == 0 and l2 > 0:
#                        firstbloodplayerlist.append(1)
#                        isdecision = True
#                    elif l1 > 0 and l2 == 0:
#                        firstbloodplayerlist.append(2)
#                        isdecision = True
#                    elif l1 == 0 and l2 == 0:
#                        firstbloodplayerlist.append(0)
#                        isdecision = True
#                    else:
#                        pass
#                        
#                else:
#                    if p1f[0] < p2f[0]:
#                        firstbloodplayerlist.append(2)
#                    elif p2f[0] < p1f[0]:
#                        firstbloodplayerlist.append(1)
#                    else:
#                        pass
#                
#                    isdecision = True
#
#firstblood_and_win_match = list()
#for gameind in enumerate(winnerplayerlist):
#    if gameind[1] != 0:
#        if gameind[1] == firstbloodplayerlist[gameind[0]]:
#            firstblood_and_win_match.append(True)
#        else:
#            firstblood_and_win_match.append(False)
#
#matchfrac = np.mean(firstblood_and_win_match)
## 3:1 odds for they player to score first (net) blood

# %%
## next up: fully tabulate win percentages as a function of (pokemon remaining 1, pokemon remaining 2)
## trivially, this should be 50% for elements along the diagonal
## but the off-diagonal elements should be interesting
#
#winnerloser_remainingpokes = list()
#
#for fel in enumerate(list_of_htmls):
#    winnerind = winnerplayerlist[fel[0]]
#        
#    if winnerind != 0: # ignore ties
#        with open(fel[1],encoding='utf-8') as htmlfile: # make utf-8 encoding explicit so that emojis can be handled
#            thismatch = list()
#    
#            soup      = BeautifulSoup(htmlfile.read(),"html.parser")
#    
#            battlog = soup.find("script",attrs={"class": "battle-log-data"})
#            btext   = battlog.get_text()
#            
#            p1faint_re = '\|faint\|p1a:[^(\||\n)]+\n'
#            p2faint_re = '\|faint\|p2a:[^(\||\n)]+\n'
#            
#            p1faint_inds     = [(m.start(0), m.end(0)) for m in re.finditer(p1faint_re, btext)]
#            p2faint_inds     = [(m.start(0), m.end(0)) for m in re.finditer(p2faint_re, btext)]
#            
#            matchstillgoing = True
#            remaining_tuple = (6,6) # this is always assumed, so don't bother appending to the list
#            
#            while matchstillgoing:
#                l1 = len(p1faint_inds)
#                l2 = len(p2faint_inds)
#                
#                if l1 != 0:
#                    p1fi = p1faint_inds[0]
#                else:
#                    p1fi = None
#                
#                if l2 != 0:
#                    p2fi = p2faint_inds[0]
#                else:
#                    p2fi = None
#                
#                if p1fi is not None and p2fi is not None:
#                    if p1fi[1] == p2fi[0] or p2fi[1] == p1fi[0]:
#                        remaining_tuple = tuple([x-1 for x in remaining_tuple])
#                        p1faint_inds = p1faint_inds[1:]
#                        p2faint_inds = p2faint_inds[1:]
#                        # print(p1faint_inds)  # for debugging
#                        # print(p2faint_inds)  # for debugging
#                    else:
#                        if p1fi[0] < p2fi[0]: # player 1 faints first
#                            if winnerind == 1:  # if player 1 is the winner, adjust the winners column
#                                remaining_tuple = (remaining_tuple[0]-1,remaining_tuple[1])
#                                # remaining_tuple[0] = remaining_tuple[0] - 1
#                            elif winnerind == 2: # if player 2 is the winner, adjust the losers column
#                                remaining_tuple = (remaining_tuple[0],remaining_tuple[1]-1)
#                                # remaining_tuple[1] = remaining_tuple[1] - 1
#                            else:
#                                pass # should never get here
#                            p1faint_inds = p1faint_inds[1:]
#                            # print(p1faint_inds)  # for debugging
#                            
#                        elif p2fi[0] < p1fi[0]: # player 2 faints first
#                            if winnerind == 1: # if player 1 is the winner, adjust the losers column
#                                remaining_tuple = (remaining_tuple[0],remaining_tuple[1]-1)
#                                # remaining_tuple[1] = remaining_tuple[1] - 1
#                            elif winnerind == 2: # if player 2 is the winner, adjust the winners column
#                                remaining_tuple = (remaining_tuple[0]-1,remaining_tuple[1])
#                                # remaining_tuple[0] = remaining_tuple[0] - 1
#                            else:
#                                pass # should never get here
#                            p2faint_inds = p2faint_inds[1:]
#                            # print(p2faint_inds)  # for debugging
#                            
#                        else:
#                            pass # this shouldn't be possible
#                            
#                elif p1fi is None and p2fi is not None: # i.e., if p2 is the only one with deaths left
#                    if winnerind == 1: # if player 1 is the winner, adjust the losers column
#                        remaining_tuple = (remaining_tuple[0],remaining_tuple[1]-1)
#                        # remaining_tuple[1] = remaining_tuple[1] - 1
#                    elif winnerind == 2: # if player 2 is (somehow) the winner (e.g., last-poke curselax followed by forfeit), adjust the winners column
#                        remaining_tuple = (remaining_tuple[0]-1,remaining_tuple[1])
#                        # remaining_tuple[0] = remaining_tuple[1] - 1
#                    else:
#                        pass # should never get here
#                    p2faint_inds = p2faint_inds[1:]
#                    # print(p2faint_inds) # for debugging
#                        
#                elif p1fi is not None and p2fi is None: # i.e., if p1 is the only one with deaths left
#                    if winnerind == 1: # if player 1 is (somehow) the winner (e.g., last-poke curselax followed by forfeit), adjust the winners column
#                        remaining_tuple = (remaining_tuple[0]-1,remaining_tuple[1])
#                        # remaining_tuple[0] = remaining_tuple[0] - 1
#                    elif winnerind == 2: # if player 2 is the winner, adjust the losers column
#                        remaining_tuple = (remaining_tuple[0],remaining_tuple[1]-1)
#                        # remaining_tuple[1] = remaining_tuple[1] - 1
#                    else:
#                        pass
#                    p1faint_inds = p1faint_inds[1:]
#                    # print(p1faint_inds)  # for debugging
#                    
#                elif p1fi is None and p2fi is None:
#                    matchstillgoing = False
#                    
#                else:
#                    pass # should never get here
#                
#                if matchstillgoing:
#                    thismatch.append(remaining_tuple)
#            
#            winnerloser_remainingpokes.append(thismatch)
                    
# %% stats on the full table computed above
#winrate_mat = 0.5*np.eye(6)
#
## rows    = winners
## columns = losers
#
#for ind1 in range(5):
#    rem1 = ind1 + 1
#    for ind2 in range(ind1+1,6):
#        rem2 = ind2 + 1
#        
#        winningpair = (rem1,rem2)
#        losingpair  = (rem2,rem1)
#        
#        wincounts  = 0
#        losecounts = 0
#        
#        for gameind in enumerate(winnerloser_remainingpokes):
#            thisgame = gameind[1]
#            
#            add_to_wc = any([x==winningpair for x in thisgame])
#            add_to_lc = any([x==losingpair for x in thisgame])
#            
#            if add_to_wc:
#                wincounts = wincounts + 1
#            else:
#                pass
#            
#            if add_to_lc:
#                losecounts = losecounts + 1
#            else:
#                pass
#            
#        
#        wrate = wincounts / (wincounts + losecounts)
#        winrate_mat[ind1,ind2] = wrate
#        winrate_mat[ind2,ind1] = 1 - wrate
#        
## basically, "first blood" brings win rate up to 3:1 odds
## when the # of pokemon goes down to 3-2 or 2-1, those odds go up to ~5.5:1
## going up by 2 brings you up to over 10:1 odds
                
# %% spikes stats

# seek matches & catalog whether the winner & loser:
# use spikes
# use spin
# use both
# use neither
# and compute the win rates of each matchup (a total of 6 winrates, as the diagonal is trivially 50% and the off-diagonal elements are mirrored & flipped about 50%)

# let's define the grid this way:
# 0: spikes
# 1: spin
# 2: both
# 3: neither
# let rows be the winning player
# let columns be the losing player
            
wincount_mat = np.zeros((4,4))
smearglecount_winner_mat = np.zeros((4,4))
smearglecount_loser_mat  = np.zeros((4,4))
elec_count_p1 = 0
elec_count_p2 = 0

lax_count_p1 = 0
lax_count_p2 = 0

spikes_count_p1 = 0
spikes_count_p2 = 0

toxic_or_thief_count_p1 = 0
toxic_or_thief_count_p2 = 0

thiefusage_tuples = list() # hmmm... this might be more complicated, as it means registering thief usage to different pokemon...

for fel in enumerate(list_of_htmls):
    winnerind = winnerplayerlist[fel[0]]
        
    if winnerind != 0: # ignore ties
        with open(fel[1],encoding='utf-8') as htmlfile: # make utf-8 encoding explicit so that emojis can be handled
            thismatch = list()
    
            soup      = BeautifulSoup(htmlfile.read(),"html.parser")
    
            battlog = soup.find("script",attrs={"class": "battle-log-data"})
            btext   = battlog.get_text()
            
            spikes_p1 = '\|move\|p1a:[^\|]+\|Spikes\|'
            spikes_p2 = '\|move\|p2a:[^\|]+\|Spikes\|'
            
            spiker_p1 = '\|switch\|p1a:[^\|]+\|(Cloyster|Forretress)'
            spiker_p2 = '\|switch\|p2a:[^\|]+\|(Cloyster|Forretress)'
            
            spin_p1   = '\|move\|p1a:[^\|]+\|Rapid Spin\|'
            spin_p2   = '\|move\|p2a:[^\|]+\|Rapid Spin\|'
            
            spinner_p1 = '\|switch\|p1a:[^\|]+\|(Starmie)'
            spinner_p2 = '\|switch\|p2a:[^\|]+\|(Starmie)'
            
            smeargle_p1 = '\|switch\|p1a:[^\|]+\|Smeargle'
            smeargle_p2 = '\|switch\|p2a:[^\|]+\|Smeargle'
            
            elec_p1     = '\|switch\|p1a:[^\|]+\|(Zapdos|Raikou)'
            elec_p2     = '\|switch\|p2a:[^\|]+\|(Zapdos|Raikou)'
            
            lax_p1      = '\|switch\|p1a:[^\|]+\|(Snorlax)'
            lax_p2      = '\|switch\|p2a:[^\|]+\|(Snorlax)'
            
            # or... JUST thief (roughly 15% usage, which is higher than I would've thought,frankly)
            toxorthief_p1 = '\|move\|p1a:[^\|]+\|(Thief)'#|Thunder Wave|Stun Spore|Sleep Powder|Lovely Kiss|Thunder|Body Slam|Sludge Bomb|Hypnosis|Sing|Spore|Dragonbreath)\|'
            toxorthief_p2 = '\|move\|p2a:[^\|]+\|(Thief)'#|Thunder Wave|Stun Spore|Sleep Powder|Lovely Kiss|Thunder|Body Slam|Sludge Bomb|Hypnosis|Sing|Spore|Dragonbreath)\|'
                        
            p1_used_spin = re.search(spin_p1,btext)
            p2_used_spin = re.search(spin_p2,btext)
            
            p1_used_spikes = re.search(spikes_p1,btext)
            p2_used_spikes = re.search(spikes_p2,btext)
            
            p1_used_spiker = re.search(spiker_p1,btext)
            p2_used_spiker = re.search(spiker_p2,btext)
            
            p1_used_spinner = re.search(spinner_p1,btext)
            p2_used_spinner = re.search(spinner_p2,btext)
            
            p1_used_smeargle = re.search(smeargle_p1,btext)
            p2_used_smeargle = re.search(smeargle_p2,btext)
            
            p1_used_elec     = re.search(elec_p1,btext)
            p2_used_elec     = re.search(elec_p2,btext)
            
            p1_used_lax      = re.search(lax_p1,btext)
            p2_used_lax      = re.search(lax_p2,btext)
            
            p1_used_toxorthief = re.search(toxorthief_p1,btext)
            p2_used_toxorthief = re.search(toxorthief_p2,btext)
            
            if p1_used_elec is not None:
                elec_count_p1 = elec_count_p1 + 1
            else:
                pass
            
            if p2_used_elec is not None:
                elec_count_p2 = elec_count_p2 + 1
            else:
                pass
            
            if p1_used_lax is not None:
                lax_count_p1 = lax_count_p1 + 1
            else:
                pass
            
            if p2_used_lax is not None:
                lax_count_p2 = lax_count_p2 + 1
            else:
                pass
            
            if p1_used_spikes is not None or p1_used_spiker is not None:
                spikes_count_p1 = spikes_count_p1 + 1
                spikes1 = True
            else:
                spikes1 = False
                
            if p2_used_spikes is not None or p2_used_spiker is not None:
                spikes_count_p2 = spikes_count_p2 + 1
                spikes2 = True
            else:
                spikes2 = False
                
            if p1_used_toxorthief is not None:# or spikes1:
                toxic_or_thief_count_p1 = toxic_or_thief_count_p1 + 1
                
            if p2_used_toxorthief is not None:# or spikes2:
                toxic_or_thief_count_p2 = toxic_or_thief_count_p2 + 1
            
            if (p1_used_spikes is not None or p1_used_spiker is not None) and (p1_used_spin is None and p1_used_spinner is None):
                p1ind = 0
            elif (p1_used_spikes is None and p1_used_spiker is None) and (p1_used_spin is not None or p1_used_spinner is not None):
                p1ind = 1
            elif (p1_used_spikes is not None or p1_used_spiker is not None) and (p1_used_spin is not None or p1_used_spinner is not None):
                p1ind = 2
            elif (p1_used_spikes is None and p1_used_spiker is None) and (p1_used_spin is None and p1_used_spinner is None):
                p1ind = 3
            else:
                pass # should never happen
                
            if (p2_used_spikes is not None or p2_used_spiker is not None) and (p2_used_spin is None and p2_used_spinner is None):
                p2ind = 0
            elif (p2_used_spikes is None and p2_used_spiker is None) and (p2_used_spin is not None or p2_used_spinner is not None):
                p2ind = 1
            elif (p2_used_spikes is not None or p2_used_spiker is not None) and (p2_used_spin is not None or p2_used_spinner is not None):
                p2ind = 2
            elif (p2_used_spikes is None and p2_used_spiker is None) and (p2_used_spin is None and p2_used_spinner is None):
                p2ind = 3
            else:
                pass # should never happen
            
            if winnerind == 1: # player 1 wins
                rowind = p1ind
                colind = p2ind
                winner_used_smeargle = p1_used_smeargle is not None
                loser_used_smeargle  = p2_used_smeargle is not None
            elif winnerind == 2: # player 2 wins
                rowind = p2ind
                colind = p1ind
                winner_used_smeargle = p2_used_smeargle is not None
                loser_used_smeargle  = p1_used_smeargle is not None
                
            wincount_mat[rowind,colind] = wincount_mat[rowind,colind] + 1
            
            smearglecount_winner_mat[rowind,colind] = smearglecount_winner_mat[rowind,colind] + winner_used_smeargle
            smearglecount_loser_mat[rowind,colind]  = smearglecount_loser_mat[rowind,colind] + loser_used_smeargle
            

totalmatch_mat = wincount_mat + np.transpose(wincount_mat)

winrate_mat = np.divide(wincount_mat,totalmatch_mat)
# okay so, when I simply count whether or not Spikes were used, there's a substantial effect of using spikes vs. not using it
# but when I count use of a conventional spiker on top of whether or not spikes were used, that effect disappears
# the strongest effect is then of pure-spin team vs. team with spikes, with the spiking team winning 57.5% of the time
# however, there are only 40 matches in which that was the case, which gives SEM of roughly 8% from a null rate of 50%
# in other words, the win rate of spikes vs. nonspikes is not significantly different from 50:50! I simply don't have a large enough sample!
# the next strongest effect is a win rate of roughly 54% for teams with both spikes + spin vs. teams with only spikes
# here, we have a sample of 104 games, which still gives SEM of roughly 5%
# which means we'd need to have a 60% winrate to have this effect be "detectable"
# the most common matchup is pure spikes vs. pure spikes. 114 of 292 (decisive) matches were this matchup.
# next most common was spikes vs. spikes + spin. 104 matches were this type.
# both teams being spikes + spin only happened 19 times.
# spikes vs. only spin only happened 40 times
# importantly, however, one team using neither spikes (or a vetted "spiker") NOR spin only accounted for 15 matches total
# in other words, almost every match played attempted to play the spikes game to some extent.
# oh jeez. when I include common spinners, the total number of games where even one side played without a spiker or spinner is only 11! eleven!!!!