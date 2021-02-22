import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from copenhagenurbandensity import *
from helsinkiurbandensity import *

def ploturbandata(dataframe, color):
    plt.plot(dataframe['cumulative population'], dataframe['density'], color=color)
    stdmove = np.max(dataframe['density']) / 50
    spacebetween = np.max(dataframe['density']) / 10
    lastprinteddensity = 1E6
    densitythr = 2000
    for ind, district in enumerate(dataframe.iterrows()):
        if (district[1]['density'] < lastprinteddensity - spacebetween
        or 'Jätkäsaari' in district[1]['district'])\
                and district[1]['density'] >= densitythr:
            # print(district[1])
            if 'Kallio' in district[1]['district']:
                move = 0
            elif 'Jätkäsaari' in district[1]['district']:
                move = -stdmove
            else:
                move = stdmove
            plt.text(district[1]['cumulative population'], district[1]['density'] + move,
                     district[1]['district'], color=color)
            lastprinteddensity = district[1]['density']
    plt.legend(['Kööpenhamina', 'Helsinki'])
    plt.xlabel('Kumulatiivinen väkikulu')
    plt.ylabel('Asukkaita neliökilometrillä')
    plt.ticklabel_format(style='plain')
    plt.tight_layout()


if __name__ == '__main__':
    copenhagen = generatecopenhagendata()
    ploturbandata(copenhagen, 'red')
    helsinki = generatehelsinkidata()
    ploturbandata(helsinki, 'blue')
    plt.plot([0, np.max(helsinki['cumulative population'])], [5000, 5000], color='tab:olive')
    plt.savefig('comparison.png')
    plt.show()
