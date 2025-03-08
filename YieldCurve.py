import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ustreasurycurve as ustc
import warnings
from rates import nelsonsiegelsvensson, discount, forward
from scipy.optimize import curve_fit
from enum import Enum


class Region(Enum):
    US = 'United States'
    # EU = 'European Union'
    # JP = 'Japan'
    # CN = 'China'
    # GB = 'United Kingdom'
    # CA = 'Canada'

class Currency(Enum):
    USD = 'United States Dollar'
    # EUR = 'Euro'
    # JPY = 'Japanese Yen'
    # CNY = 'Chinese Yuan'
    # GBP = 'British Pound'
    # CAD = 'Canadian Dollar'

class Compounding(Enum):
    CONTINUOUS = 'Continuous'
    WEEKLY = 'Weekly'
    BIWEEKLY = 'Bi-Weekly'
    MONTHLY = 'Monthly'
    QUARTERLY = 'Quarterly'
    SEMIANNUAL = 'Semi-Annual'
    ANNUAL = 'Annual'

class InterpolationType(Enum):
    SPOT = 'Spot'
    DISCOUNT = 'Discount'
    FORWARD = 'Forward'



class YieldCurve:

    def __init__(self, region, currency, date, compounding = Compounding.CONTINUOUS):
        # Validate region
        try:
            self.region = Region(region) if isinstance(region, str) else region
        except ValueError:
            valid_regions = ', '.join(e.value for e in Region)
            raise ValueError(f'Invalid region: {region}. Choose from {valid_regions}')

        # Validate currency
        try:
            self.currency = Currency(currency) if isinstance(currency, str) else currency
        except ValueError:
            valid_currencies = ', '.join(e.value for e in Currency)
            raise ValueError(f'Invalid currency: {currency}. Choose from {valid_currencies}')

        # Validate compounding
        try:
            self.compounding = Compounding(compounding) if isinstance(compounding, str) else compounding
        except ValueError:
            valid_compoundings = ', '.join(e.value for e in Compounding)
            raise ValueError(f'Invalid compounding type: {compounding}. Choose from {valid_compoundings}')
        
        self.date = date
        print(self.__repr__())
        self.spotrates = self._load_spots()
        self.nssparams = self._calculate_params()

    def __repr__(self):
        return f'YieldCurve(region = {self.region}, currency = {self.currency}, date = {self.date}, compounding = {self.compounding})'
    
    def __str__(self):
        return f'{self.region} Yield Curve ({self.date})'
    
    def _load_spots(self):
        TENORMAP = {'1m':1/12,'2m':1/6,'3m':0.25,'6m':0.5,'1y':1,'2y':2,'3y':3,'5y':5,'10y':10,'20y':20,'30y':30}

        if self.region == 'United States':
            warnings.simplefilter('ignore', category = UserWarning)
            ts = ustc.nominalRates(date_start = self.date, date_end = self.date)
            warnings.simplefilter('default', category = UserWarning)
            ts = ts.iloc[:,1:].melt(var_name = 'tenor', value_name = 'spot')
            ts['time'] = ts['tenor'].map(TENORMAP)
            return ts[['tenor','time','spot']].dropna()
        
    def _calculate_params(self, initial = None):
        ts = self.spotrates

        if initial is None:
            initial = [0.03, -0.02, 0.01, 0.05, 2.0, 5.0]
        
        try:
            return curve_fit(nelsonsiegelsvensson, ts['time'], ts['spot'], p0 = initial)[0]
        except RuntimeError:
            warnings.warn('Curve fitting failed to converge. Returning None.', RuntimeWarning)
            return None

    
    def interpolate(self, t, type):
        try:
            type = InterpolationType(type)
        except ValueError:
            valid_types = ', '.join(e.value for e in InterpolationType)
            raise ValueError(f'Invalid type: {type}. Choose from {valid_types}')
        
        if type == InterpolationType.SPOT:
            return nelsonsiegelsvensson(t, *self.nssparams)
        elif type == InterpolationType.DISCOUNT:
            return discount(t, nelsonsiegelsvensson(t, *self.nssparams), self.get_compounding())
        elif type == InterpolationType.FORWARD:
            spots = nelsonsiegelsvensson(t, *self.nssparams)
            return [forward(timeA = t[i], rateA = spots[i], timeB = t[i] + 1, rateB = nelsonsiegelsvensson(t[i] + 1, *self.nssparams), compounding = self.compounding) for i in range(len(t))]
    
    def plot(self, type = 'spot'):
        custom = {'axes.edgecolor':'#505258', 'grid.linestyle':'dashed', 'grid.color':'white', 'axes.facecolor':'#E8E9EB'}
        sns.set_style('whitegrid', rc = custom)
        COLORMAP = {'spot':'#4062BB','discount':'#357266','forward':'#FF495C'}
        TITLEMAP = {'spot':'Spot Rate','discount':'Discount Factor','forward':'Forward Rate'}
        ts = self.spotrates
        ts[type] = self.interpolate(ts['time'], type)
        t = np.linspace(0, np.max(ts['time']), 100)
        y = self.interpolate(t, type)
        plt.figure(figsize = (12,8))
        sns.lineplot(x = t, y = y, linestyle = '-', linewidth = 2, color = COLORMAP[type])
        sns.scatterplot(x = ts['time'], y = ts[type], marker = 'o', s = 75, color = COLORMAP[type]) 
        plt.title(f'{self.region} {TITLEMAP[type]} Term Structure ({self.date})')
        plt.xlabel('Maturity')
        plt.ylabel(TITLEMAP[type])
        plt.grid(True, axis = 'y')
        plt.show()


    
# yc = YieldCurve('United States','USD','2020-01-02')
# print(yc.get_spotrates())
# yc.plot(type = 'spot')
# yc.plot(type = 'discount')
# yc.plot(type = 'forward')	