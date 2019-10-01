# Shania Ie and Pooja Pathak
# CIS 41B
# Lab 3

"""
Description:
Part A
Fetch data from the URL and extract each country name and its associated popular names. It is saved
to a data structure (dictionary: key = country, values = list of names) and stored in a JSON file

Part B
Read data from the JSON file and store into an SQLite database. Each row of the database is for 1 country.
"""
import requests
from bs4 import BeautifulSoup
import re
import sys
import json
import sqlite3

# PART A
def createCountryDict():
    '''
    createCountryDict:
    Reads in data from website, calls a function to parse it and store the country and list of names in the data structure.
    The data is then stored in a JSON file.
    '''
    page = requests.get('https://en.wikipedia.org/wiki/List_of_most_popular_given_names')
    soup = BeautifulSoup(page.content, 'lxml')
    
    countryDict = {}
    for tag in soup.find_all('tr'):
        myStr = tag.get_text().encode(sys.stdout.encoding, errors='ignore').decode(sys.stdout.encoding)
        countryName, names = nameList(myStr)
        if countryName != '':
            if countryName not in countryDict:
                countryDict[countryName] = names
            else:
                countryDict[countryName] = countryDict[countryName] + names
    with open('data.json', 'w') as fh:
        json.dump(countryDict, fh, indent = 3)     
        
def nameList(myStr):
    '''
    nameList:
    Receives a row of the data from the website, parses the country name and the popular names.
    Returns the country name and list of popular names.
    '''
    strList = myStr.split('\n')
    m = re.search('(\w+[^\S\n]?\w+[^\S\n]?\w+)',strList[1])
    countryName = m.group()
    names = []
    if countryName != 'Region':
        for elem in strList[2:]:
            if elem!= 'NA' and elem != '':
                names.extend(elem.split(','))
    else:
        countryName = ''
        names = ''
    return (countryName, names)

# PART B
def createDatabase():
    '''
    createDatabase:
    Opens the JSON file and reads in the data. Create a table in the database with the given information.
    Each row is designated for one country. The number of columns is the maximum number of popular names.
    '''
    with open('data.json', 'r') as fh:
        d = json.load(fh) 
    conn = sqlite3.connect('Country.db')
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS CountryDB")
    cur.execute('''CREATE TABLE CountryDB(             
                       country TEXT,
                       name0 TEXT)''')   
    
    nameList = ['name'+str(i) for i in range(max([len(elem) for elem in d.values()]))]
    
    for i in range(len(nameList)- 1):
        cur.execute('''ALTER TABLE CountryDB ADD COLUMN {} TEXT'''\
                    .format(nameList[i+1]))
    
    for k,v in d.items():
        cur.execute('INSERT INTO CountryDB (country) VALUES (?)',(k,))
        for i in range(len(d[k])):
            cur.execute('UPDATE CountryDB SET {} = "{}" WHERE country = "{}"'.format(nameList[i], v[i], k))
    
    conn.commit()
    
def main():
    #createCountryDict()
    createDatabase()

main()