"""
Fetch population information from urban areas in Copenhagen from Wikipedia, and plot the urban plot
"""

import requests
from bs4 import BeautifulSoup
import bs4
import pandas as pd
import numpy as np
import re
import matplotlib.pylab as plt

wikipedia = 'https://en.wikipedia.org/'

# '<body class="mediawiki ltr sitedir-ltr mw-hide-empty-elt ns-0 ns-subject mw-editable page-Copenhagen_Municipality rootpage-Co
# penhagen_Municipality skin-vector action-view skin-vector-legacy">'

def writesoup(soup, filename):
    with open(filename, 'w') as f:
        f.write(soup.prettify())

def findnumber(string, tag):
    number = re.split('\s|,\s', string.split(tag)[1])[0].replace(',', '')
    try:
        number = float(number)
    except:
        try:
            number = float(number.split('.')[0])
        except:
            try:
                number = float(number.split('[')[0])
            except:
                print(f"couldn't parse the number from '{number}'")
                print(string)

    return number


def extractareaandpopulation(link):
    soup = BeautifulSoup(requests.get(link).text, 'html.parser')
    foundarea = False
    foundpopulation = False
    for line in soup.get_text().split('\n'):
        if 'This article is about' not in line:
            if 'area of' in line:
                area = findnumber(line, 'area of ')
                foundarea = True
                if foundpopulation:
                    break
            if 'population of' in line:
                population = findnumber(line, 'population of ')
                foundpopulation = True
                if foundarea:
                    break
    return area, population


def findareaandpopulation(soup):
    # with open('copenhagen.html', 'w') as f:
    #     f.write(soup.prettify())

    sidebox = soup.findAll("body", class_="mediawiki")

    information = []
    if len(sidebox):
        rows = sidebox[0].findAll("tr")
    for row in rows:
        if 'Districts' in row.get_text():
            districts = row.find("ul").findAll("li")
            for district in districts:
                if 'Districts' in district.get_text():
                    break
                link = district.find("a")
                area, population = extractareaandpopulation(wikipedia + link.attrs['href'])
                information.append([link.text, area, population])
    return information

def findnumberinbox(string):
    try:
        number = float(string.split()[0].split('[')[0].replace(',', ''))
    except Exception as e:
        print(e)
        exit(-1)

    return number

def extractareaandpopulationfrombox(link):
    soup = BeautifulSoup(requests.get(link).text, 'html.parser')
    sidebox = soup.findAll("body", class_="mediawiki")

    if len(sidebox):
        rows = sidebox[0].findAll("tr")

    foundarea = False
    foundpopulation = False
    areabox = False
    populationbox = False
    area = 0
    population = 0

    for row in rows:
        if areabox:
            area = findnumberinbox(row.contents[1].get_text())
            areabox = False
            foundarea = True
        if populationbox:
            population = findnumberinbox(row.contents[1].get_text())
            populationbox = False
            foundpopulation = True
        if 'Area' in row.get_text():
            areabox = True
        if 'Population' in row.get_text():
            populationbox = True
        if foundarea and foundpopulation:
            break

    if not area or not population:
        print("didn't find population or area")

    return area, population


def findurbanareaandpopulation(soup):
    ul = soup.findAll("ul")
    li = ul[1].findAll("li") # the list of neighbouring municipalities is the second list on the wiki page
    started = False
    information = []
    for item in li:
        if 'started':
            if 'Copenhagen' not in item.text and 'Greve Strand' not in item.text:
                area, population = extractareaandpopulationfrombox(wikipedia + item.contents[0].attrs['href'])
                information.append([item.contents[0].attrs['title'], area, population])
                print(information[-1])
        if 'large area of western Amager is unpopulated' in item.text:
            started = True
        if 'Vallensb' in item.text:
            started = False

    return information

def shorten(string):
    return string.replace(' Municipality', '')

def generatecopenhagendata():
    # City of Copenhagen
    copenhagenurl = 'https://en.wikipedia.org/wiki/Copenhagen_Municipality'
    page = requests.get(copenhagenurl)
    soup = BeautifulSoup(page.text, 'html.parser')
    information = findareaandpopulation(soup)
    # Copenhagen area
    urbanurl = 'https://en.wikipedia.org/wiki/Urban_area_of_Copenhagen'
    page = requests.get(urbanurl)
    soup = BeautifulSoup(page.text, 'html.parser')
    urbaninf = findurbanareaandpopulation(soup)
    information = information + urbaninf
    information = pd.DataFrame.from_records(information, columns=['district', 'area', 'population'])
    information['density'] = information['population'] / information['area']
    information = information.sort_values('density', ascending=False)
    information['cumulative population'] = np.cumsum(information['population'])

    return information
if __name__ == '__main__':
    dataframe = generatecopenhagendata()

    dataframe.plot('cumulative population', 'density')
    move = np.max(dataframe['density']) / 50
    spacebetween = np.max(dataframe['density']) / 10
    lastprinteddensity = 1E6
    for ind, district in enumerate(dataframe.iterrows()):
        # if ind < 5 or ind % 7 == 0:
        #     if district[1]['district'] == 'Sundbyvester':
        #         move = 0
        #     elif district[1]['district'] == 'Bispebjerg':
        #         move = np.max(information['density']) / 25
        #     else:
        #         move = np.max(information['density']) / 50
        if district[1]['density'] < lastprinteddensity - spacebetween:
            plt.text(district[1]['cumulative population'], district[1]['density'] + move,
                     shorten(district[1]['district']))
            lastprinteddensity = district[1]['density']
    plt.tight_layout()
    plt.show()
