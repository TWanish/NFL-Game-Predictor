#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 18:35:07 2019

@author: TMWanish

Used for actually predicting games for the next week or adhoc game predictions
"""

import pandas as pd
import os
from modelGeneration import getModel
from gamePredictions import predictNextWeek

try:
    path = os.path.normpath(str(os.getcwd()).split('lib')[0]+'/data/teamData.json')
except:
    print('path not found')
    

data = pd.read_json(path)
    
model = getModel(data)

predictNextWeek(model, data, 8, False, file_path = path)