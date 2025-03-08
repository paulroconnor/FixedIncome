import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ustreasurycurve as ustc
import warnings
import fixedincomeutils as fi
import validation as v
from scipy.optimize import curve_fit
from enums import Compounding, Region, Currency, InterpolationType, Calendar



class YieldCurve:

    def __init__(self, region, date, compounding, currency = None, calendar = None):
        self.region = v.validate_enum(region, Region, 'region')
        self.currency = v.validate_enum(currency, Currency, 'currency') if currency else v.default_currency(self.region)
        self.calendar = v.validate_enum(calendar, Calendar, 'calendar') if calendar else v.default_calendar(self.region)
        self.compounding = v.validate_enum(compounding, Compounding, 'compounding')
        self.date = v.validate_date(date, self.calendar)
        print(self.__repr__())
        self.spotrates = self._load_spots()
        self.nssparams = self._calculate_params()


    def __repr__(self):
        return f'YieldCurve(region = {self.region.value}, date = {self.date.date()}, compounding = {self.compounding.value}, currency = {self.currency.value}, calendar = {self.calendar.value})'


    def _load_spots(self):
        TENORMAP = {'1m':1/12,'2m':1/6,'3m':0.25,'6m':0.5,'1y':1,'2y':2,'3y':3,'5y':5,'10y':10,'20y':20,'30y':30}
        if self.region == Region.US:
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
            return curve_fit(fi.nelsonsiegelsvensson, ts['time'], ts['spot'], p0 = initial)[0]
        except (RuntimeError, ValueError) as e:
            warnings.warn(f'Curve fitting failed: {e}', RuntimeWarning)
        return None

    
    def interpolate(self, t, type):
        type = v.validate_enum(type, InterpolationType, 'type')
        if type == InterpolationType.SPOT:
            return fi.nelsonsiegelsvensson(t, *self.nssparams)
        elif type == InterpolationType.DISCOUNT:
            return fi.discount(t, fi.nelsonsiegelsvensson(t, *self.nssparams), self.compounding)
        elif type == InterpolationType.FORWARD:
            spots = fi.nelsonsiegelsvensson(t, *self.nssparams)
            return [fi.forward(timeA = t[i], rateA = spots[i], timeB = t[i] + 1, rateB = fi.nelsonsiegelsvensson(t[i] + 1, *self.nssparams), compounding = self.compounding) for i in range(len(t))]
    

    def plot(self, type):
        PLOTSTYLE = {'axes.edgecolor':'#505258', 'grid.linestyle':'dashed', 'grid.color':'white', 'axes.facecolor':'#E8E9EB'}
        sns.set_style('whitegrid', rc = PLOTSTYLE)
        COLORMAP = {'Spot Rate':'#4062BB','Discount Factor':'#357266','Forward Rate':'#FF495C'}
        ts = self.spotrates
        ts[type] = self.interpolate(ts['time'], type)
        t = np.linspace(0, np.max(ts['time']), 100)
        y = self.interpolate(t, type)
        plt.figure(figsize = (12,8))
        sns.lineplot(x = t, y = y, linestyle = '-', linewidth = 2, color = COLORMAP[type])
        sns.scatterplot(x = ts['time'], y = ts[type], marker = 'o', s = 75, color = COLORMAP[type]) 
        plt.title(f'{self.region.value} {type} Term Structure ({self.date.date()})')
        plt.xlabel('Maturity')
        plt.ylabel(type)
        plt.grid(True, axis = 'y')
        plt.show()


    
# yc = YieldCurve(region = 'United States', date = '2025-01-13', compounding = 'Continuous')
# print(yc.spotrates)
# yc.plot(type = 'Spot Rate')
# yc.plot(type = 'Discount Factor')
# yc.plot(type = 'Forward Rate')	
