"""
Fetch population information from urban areas in Helsinki from Paavo, and plot the urban plot
"""

import pandas as pd
import numpy as np
import matplotlib.pylab as plt

def readandprepare(filename):
    data = pd.read_csv(filename, delimiter=';', skiprows=2, encoding='ISO-8859-15')
    data = data[['Postinumeroalue', 'Postinumeroalueen pinta-ala', 'Asukkaat yhteensä, 2019 (HE)']]
    data = data.rename(columns={'Postinumeroalue': 'district',
                                'Postinumeroalueen pinta-ala': 'area',
                                'Asukkaat yhteensä, 2019 (HE)': 'population'})
    data = data[data.apply(lambda x: x['district'].startswith(('00', '01', '02', )), axis=1)]
    data['district'] = [x.split(' ', 1)[1] for x in data['district']]
    data['area'] = data['area'] / 1E6
    data['density'] = data['population'] / data['area']
    data = data.sort_values('density', ascending=False)
    data['cumulative population'] = np.cumsum(data['population'])

    return data

def generatehelsinkidata():
    filename = 'data/009_12f7_2021.csv'
    information = readandprepare(filename)
    return information


if __name__ == '__main__':
    information = generatehelsinkidata()
    information.plot('cumulative population', 'density')
    move = np.max(information['density']) / 50
    spacebetween = np.max(information['density']) / 10
    lastprinteddensity = 1E6
    for ind, district in enumerate(information.iterrows()):
        if district[1]['density'] < lastprinteddensity - spacebetween:
            plt.text(district[1]['cumulative population'], district[1]['density'] + move,
                     district[1]['district'])
            lastprinteddensity = district[1]['density']
    plt.tight_layout()
    plt.show()
