#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 08:15:43 2019

@author: p2854292
"""

import requests
import bs4
import json
import os
import pandas as pd

def updateTeamInfo(teamData, link, name = None):
    utRes = requests.get(link)
    utHtml = utRes.content
    utSoup = bs4.BeautifulSoup(utHtml, 'html.parser')
    ## Summary Data (pts For, pts Against, SRS, SOS)
    utStep = utSoup.find('div', attrs={'data-template':'Partials/Teams/Summary'}).findAll('p')
    alias = utSoup.find('div', attrs={'data-template':
        'Partials/Teams/Summary'}).findAll('span')[1].getText()
    ptsF = utStep[2].getText().split(' ')[3].split('(')[1].split('/')[0]
    ptsA = utStep[3].getText().split(' ')[3].split('(')[1].split('/')[0]
    srs = utStep[5].getText().split(' ')[1]
    sos = utStep[5].getText().split(' ')[7][0:-1]
    toAppend = {
            name:{
            'alias':alias,
            'link':link,
            'ptsF':ptsF,
            'ptsA':ptsA,
            'srs':srs,
            'sos':sos,
                 }
               }
    ## Summary Data (Off Rush yards, Pass Yards, YPP, Penalties, TO)
    utStep2 = utSoup.find('table', attrs={'id':'team_stats'})
    utStep3 = bs4.BeautifulSoup(str(utStep2.findAll('tbody')),'html.parser').findAll('tr')
    offensiveStats = utStep3[0].findAll('td')
    defensiveStats = utStep3[1].findAll('td')
    ## Offensive Stats
    for i in range(0,len(offensiveStats)):
        stat = offensiveStats[i]['data-stat']
        if stat == 'g':
            continue
        value = offensiveStats[i].getText()
        try:
            if len(value.split('Own'))>1:
                value = value.split('Own ')[1]
        except:
            pass
        try:
            if len(value.split(':'))>1:
                minutes = value.split(':')[0]
                seconds = value.split(':')[1]
                value = (float(minutes)*60+float(seconds))/60
        except:
            pass
        toAppend[name].update({'off_'+stat:value})
    for j in range(0,len(defensiveStats)):
        stat = defensiveStats[j]['data-stat']
        if stat == 'g':
            continue
        value = defensiveStats[j].getText()
        try:
            if len(value.split('Own'))>1:
                value = value.split('Own ')[1]
        except:
            pass
        try:
            if len(value.split(':'))>1:
                minutes = value.split(':')[0]
                seconds = value.split(':')[1]
                value = (float(minutes)*60+float(seconds))/60
        except:
            pass
        toAppend[name].update({'def_'+stat:value})
    teamData.update(toAppend)
    return

path = os.path.normpath(str(os.getcwd()).split('lib')[0]+'/data/teamData.json')

teamData = {}

try:
    data = pd.read_json(path)
    teamData = data.to_dict()
    print('Found Existing Data File')
    for team in list(teamData.keys()):
        updateTeamInfo(teamData, teamData[team]['link'])
        print('Updating ' + team)
    
except:
    print('Existing data file not found')
    url = 'https://www.pro-football-reference.com/teams/'
    res = requests.get(url)
    html = res.content
    soup = bs4.BeautifulSoup(html, 'html.parser')
    step1 = soup.find('table', attrs={'id':'teams_active'})
    step2 = bs4.BeautifulSoup(str(step1.findAll('tbody')),'html.parser').findAll('tr')
    
    for i in range(0,len(step2)):
        year = bs4.BeautifulSoup(str(step2[i].find('td',
                                     attrs={'data-stat':'year_max'})),'html.parser').string
        if year == '2019' and not step2[i].has_attr('class'):
            teamLink = bs4.BeautifulSoup(str(step2[i].find('th',
                                           attrs={'data-stat':'team_name'})),'html.parser').find('a', href=True)
            name = teamLink.string
            print('Fetching ' + name)
            link = 'https://www.pro-football-reference.com'+teamLink['href']+'2019.htm'
            updateTeamInfo(teamData, link, name)
        
## Getting Schedule Results
print('Updating Schedule Results...')
url = 'https://www.pro-football-reference.com/years/2019/games.htm'
res = requests.get(url)
html = res.content
soup = bs4.BeautifulSoup(html, 'html.parser')
schedStep1 = soup.find('table', attrs={'id':'games'})
schedStep2 = bs4.BeautifulSoup(str(schedStep1.findAll('tbody')),'html.parser').findAll('tr')

resultsData = {}

for i in range(0,len(schedStep2)):
    week = 'week-'+bs4.BeautifulSoup(str(schedStep2[i].find('th',
                                         attrs={'data-stat':'week_num'})),'html.parser').string
    try:
        team1 = bs4.BeautifulSoup(str(schedStep2[i].find('td', 
                                      attrs={'data-stat':'winner'})),'html.parser').find('a').string
    except:
        continue
    try:
        if 'winning-score' in teamData[team1][week].keys():
            continue
        else:
            raise ValueError('Not present for '+ week)
    except:
        team1Score = bs4.BeautifulSoup(str(schedStep2[i].find('td',
                                           attrs={'data-stat':'pts_win'})),'html.parser').string
        if team1Score is None:
            print('done.')
            break
        
        if bs4.BeautifulSoup(str(schedStep2[i].find('td',
                                 attrs={'data-stat':'game_location'})),'html.parser').string == "@":
            team1Home = False
        else:
            team1Home = True
        try:
            team2 = bs4.BeautifulSoup(str(schedStep2[i].find('td',
                                          attrs={'data-stat':'loser'})),'html.parser').find('a').string
        except:
            continue
        team2Score = bs4.BeautifulSoup(str(schedStep2[i].find('td',
                                           attrs={'data-stat':'pts_lose'})),'html.parser').string
        
        results = {
                week:
                    {
                        'winning-team':team1,
                        'winning-score': team1Score,
                        'winning-team-home':team1Home,
                        'losing-team':team2,
                        'losing-score':team2Score
                    }
                }
        try:
            existingWeek = teamData[team1][week]
        except:
            existingWeek = {}
        existingWeek.update(results)
        try:
            teamData[team1].update(existingWeek)
        except:
            for team in teamData.keys():
                if team1 in teamData[team]['alias']:
                    team1 = team
                    teamData[team1].update(existingWeek)
                    break
        try:
            teamData[team2].update(existingWeek)
        except:
            for team in teamData.keys():
                if team2 in teamData[team]['alias']:
                    team2 = team
                    teamData[team2].update(existingWeek)
                    break
    
with open(path, 'w') as outfile:
    json.dump(teamData, outfile)