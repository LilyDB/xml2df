# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 11:22:15 2021

@author: PHOL
"""

import xml.etree.ElementTree as ET
import pandas as pd
import os

filename = 'restnoteringar-2-0.xml'
xtree = ET.parse(filename)
root = xtree.getroot()

# Helper funtions
def getName(name):
    # split tag, only take the part after }   
    result = name
    splitArr = name.split('}')
    if len(splitArr) > 1:
        result = splitArr[1]
    return result

def insertKeyValue(root):
    if len(list(root)) > 0:
        for child in root:
            insertKeyValue(child)
    else:
        # Iterate through root to get name (tag) and value (text)
        key = getName(root.tag)
        value = root.text + " "
        # if there are several values, seperate them by \n for pre-processing later
        if key in columItem.keys():
            columItem[key] = columItem[key] + "\n" + value
        else:
            columItem[key] = value


# Initialize
keyvalueList = [] # to get key-value (tag- text) list
maxColumCount = 0 # to create number of columns equal to number of keys later
maxColumIndex = 0 # to get key position later
i = 0

# Find key value in each main child of each Supply Shortage root
for eachSupplyShortagePublic in root:

    columItem = {}
    # insert key value pairs for each single root
    for mainChild in eachSupplyShortagePublic:
        insertKeyValue(mainChild)

    # count number of main child and indexing 
    if len(columItem.keys()) > maxColumCount:
       maxColumCount = len(columItem.keys())
       maxColumIndex = i

    keyvalueList.append(columItem)
    i += 1

# Find key-value for each sub child and append all in a dictionary
dict = {}

if len(keyvalueList) > 0:
    #Get key position by index of keyvalueList 
    mainKeys = keyvalueList[maxColumIndex].keys()
    #Create list of temporary keys
    for tempKey in mainKeys:
        dict[tempKey] = []

    # For loop within keyvalueList
    for i in range(0, len(keyvalueList)):
        column = keyvalueList[i]
        columnKeys = column.keys()

        for key in mainKeys:
            # Put key value into dict if exist
            if key in columnKeys:
                dict[key].append(column[key])
            # else, append empty value
            else:
                dict[key].append("")
else: # if no keyvalue was found
  raise ValueError('There is no data')

# Get dataframe
stockoutse = pd.DataFrame(dict)

stockoutse = stockoutse[['NplPackId','ForecastStartDate','ActualEndDate']]

sub_single = stockoutse[~stockoutse['NplPackId'].str.contains("\n")]

multi_rowdf = stockoutse[stockoutse['NplPackId'].str.contains("\n")]


sub1 = multi_rowdf[['NplPackId','ForecastStartDate','ActualEndDate']]

sub1 = sub1.assign(NplPackId=sub1.NplPackId.str.split('\n'))\
          .explode('NplPackId')\
          .reset_index(drop=True)
sub2  = sub1.assign(ForecastStartDate=sub1.ForecastStartDate.str.split('\n'))\
            .explode('ForecastStartDate')\
            .reset_index(drop=True)
sub3  = sub2.assign(ActualEndDate=sub2.ActualEndDate.str.split('\n'))\
            .explode('ActualEndDate')\
            .reset_index(drop=True)

sub4 = sub3[['NplPackId','ForecastStartDate','ActualEndDate']]
sub_multi = sub4.drop_duplicates().reset_index(drop=True)


se = sub_multi.append(sub_single, ignore_index=True)
se.sort_values(by='ForecastStartDate')

file = r'C:/Users/phol/Desktop/stockout_se.csv'
if os.path.exists(file):
    os.remove(file)
    se.to_csv(file,index=False)
    print('number of records: ' + str(len(se)))
    print("done")

