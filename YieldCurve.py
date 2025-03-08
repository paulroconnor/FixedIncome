import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ustreasurycurve as ustc
import warnings
from rates import nelsonsiegelsvensson, discount, forward
from scipy.optimize import curve_fit

class YieldCurve:

    def __init__(self, region, currency, date, compounding = 'continuous'):
        self.region = region
        self.currency = currency
        self.date = date
        self.compounding = compounding
        print(self.__repr__())
        self.spotrates = self._load_spots()
        self.nssparams = self._calculate_params()
        YieldCurve._set_styling()

    def __repr__(self):
        return f'YieldCurve(region = {self.region}, currency = {self.currency}, date = {self.date}, compounding = {self.compounding})'
    
    def __str__(self):
        return f'{self.region} Yield Curve ({self.date})'
    
    def get_region(self):
        return self.region
    
    def get_currency(self):
        return self.currency
    
    def get_date(self):
        return self.date
    
    def get_compounding(self):
        return self.compounding
    
    def get_spotrates(self):
        return self.spotrates
    
    def get_nssparams(self):
        return self.nssparams
    
    def _load_spots(self):
        TENORMAP = {'1m':1/12,'2m':1/6,'3m':0.25,'6m':0.5,'1y':1,'2y':2,'3y':3,'5y':5,'10y':10,'20y':20,'30y':30}

        if self.get_region() == 'United States':
            warnings.simplefilter('ignore', category = UserWarning)
            ts = ustc.nominalRates(date_start = self.get_date(), date_end = self.get_date())
            warnings.simplefilter('default', category = UserWarning)
            ts = ts.iloc[:,1:].melt(var_name = 'tenor', value_name = 'spot')
            ts['time'] = [TENORMAP[tenor] for tenor in ts['tenor']]
            return ts[['tenor','time','spot']].dropna()
        
    def _calculate_params(self):
        ts = self.get_spotrates()
        return curve_fit(nelsonsiegelsvensson, ts['time'], ts['spot'], p0 = [0.03, -0.02, 0.01, 0.05, 2.0, 5.0])[0]
    
    def interpolate(self, t, type):
        if type == 'spot':
            return nelsonsiegelsvensson(t, *self.get_nssparams())
        elif type == 'discount':
            return discount(t, nelsonsiegelsvensson(t, *self.get_nssparams()), self.get_compounding())
        elif type == 'forward':
            spots = nelsonsiegelsvensson(t, *self.get_nssparams())
            return [forward(timeA = t[i], rateA = spots[i], timeB = t[i] + 1, rateB = nelsonsiegelsvensson(t[i] + 1, *self.get_nssparams()), compounding = self.get_compounding()) for i in range(len(t))]
    
    @staticmethod
    def _set_styling():
        custom = {'axes.edgecolor':'#505258', 'grid.linestyle':'dashed', 'grid.color':'white', 'axes.facecolor':'#E8E9EB'}
        sns.set_style('whitegrid', rc = custom)
    
    def plot(self, type = 'spot'):
        COLORMAP = {'spot':'#4062BB','discount':'#357266','forward':'#FF495C'}
        TITLEMAP = {'spot':'Spot Rate','discount':'Discount Factor','forward':'Forward Rate'}

        ts = self.get_spotrates()
        ts[type] = self.interpolate(ts['time'], type)
        t = np.linspace(0, np.max(ts['time']), 100)
        y = self.interpolate(t, type)

        plt.figure(figsize = (12,8))
        sns.lineplot(x = t, y = y, linestyle = '-', linewidth = 2, color = COLORMAP[type])
        sns.scatterplot(x = ts['time'], y = ts[type], marker = 'o', s = 75, color = COLORMAP[type]) 
        plt.title(f'{self.get_region()} {TITLEMAP[type]} Term Structure ({self.get_date()})')
        plt.xlabel('Maturity')
        plt.ylabel(TITLEMAP[type])
        plt.grid(True, axis = 'y')
        plt.show()


    
# yc = YieldCurve('United States','USD','2020-01-02')
# print(yc.get_spotrates())
# yc.plot(type = 'spot')
# yc.plot(type = 'discount')
# yc.plot(type = 'forward')	