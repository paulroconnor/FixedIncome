import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from yieldcurve import YieldCurve
from enums import Compounding, Region, Currency, Calendar, Frequency, Convention
import validation as v
import fixedincomeutils as fi

class InterestRateSwap:
    def __init__(self, notional, fixedrate, frequency, maturitydate, valuationdate, compounding, convention, region, currency = None, calendar = None):
        self.notional = notional
        self.fixedrate = fixedrate
        self.frequency = v.validate_enum(frequency, Frequency, 'frequency')
        self.region = v.validate_enum(region, Region, 'region')
        self.currency = v.validate_enum(currency, Currency, 'currency') if currency else v.default_currency(self.region)
        self.calendar = v.validate_enum(calendar, Calendar, 'calendar') if calendar else v.default_calendar(self.region)
        self.compounding = v.validate_enum(compounding, Compounding, 'compounding')
        self.convention = v.validate_enum(convention, Convention, 'convention')
        self.maturitydate = v.validate_date(maturitydate, self.calendar)
        self.valuationdate = v.validate_date(valuationdate, self.calendar)
        print(self.__repr__())
        self.paymentdates = self._paymentdates()
        self.paymenttimes = self._paymenttimes()
        self.yieldcurve = YieldCurve(self.region, self.valuationdate, self.compounding, self.currency, self.calendar)
        self.discountfactors = self._discountfactors()
        self.fixedcashflows = self._fixedcashflows()
        self.floatingcashflows = self._floatingcashflows()
        self.fixedprice = self._price('Fixed')
        self.floatingprice = self._price('Floating')
        self.npv = self.fixedprice - self.floatingprice
        self.fixedvaluationtable = self._valuationtable('Fixed')
        self.floatingvaluationtable = self._valuationtable('Floating')
        self.fixedduration = self._duration('Fixed')
        self.floatingduration = self._duration('Floating')
        self.fixedconvexity = self._convexity('Fixed')
        self.floatingconvexity = self._convexity('Floating')
    
    def __repr__(self):
        return f'InterestRateSwap(notional = {self.notional:,}, fixedrate = {self.fixedrate :.2%}, frequency = {self.frequency.value}, maturitydate = {self.maturitydate.date()}, valuationdate = {self.valuationdate.date()}, region = {self.region.value}, currency = {self.currency.value}, compounding = {self.compounding.value}, calendar = {self.calendar.value}, convention = {self.convention.value})'
    
    def _paymentdates(self):
        dates = fi.dateschedule(self.valuationdate, self.maturitydate, self.frequency.value)
        return fi.businessdayadjust(dates, self.calendar.value)

    def _paymenttimes(self):
        return fi.datetotime(self.paymentdates, self.valuationdate, self.convention.value)
    
    def _fixedcashflows(self):
        FREQMAP = {'Weekly':52, 'Monthly':12, 'Quarterly':4, 'Semi-Annual':2, 'Annual':1}
        return [self.notional * self.fixedrate / FREQMAP.get(self.frequency.value, None)] * len(self.paymentdates)
    
    def _floatingcashflows(self):
        FREQMAP = {'Weekly':52, 'Monthly':12, 'Quarterly':4, 'Semi-Annual':2, 'Annual':1}
        rates = self.yieldcurve.interpolate(self.paymenttimes, 'Forward Rate')
        return self.notional * np.asarray(rates) / FREQMAP.get(self.frequency.value, None)

    def _discountfactors(self):
        return self.yieldcurve.interpolate(self.paymenttimes, 'Discount Factor')
    
    def _price(self, leg):
        cashflows = np.asarray(self.fixedcashflows, dtype = float) if leg == 'Fixed' else np.asarray(self.floatingcashflows, dtype = float)
        discountfactors = np.asarray(self.discountfactors, dtype = float)
        return cashflows @ discountfactors
    
    def _valuationtable(self, leg):
        return pd.DataFrame({
            'Payment Date': self.paymentdates,
            'Time': self.paymenttimes,
            'Cash Flow': self.fixedcashflows if leg == 'Fixed' else self.floatingcashflows,
            'Discount Factor': self.discountfactors,
            'Present Value': (self.fixedcashflows if leg == 'Fixed' else self.floatingcashflows) * self.discountfactors
        })
    
    def _duration(self, leg):
        cashflows = self.fixedcashflows if leg == 'Fixed' else self.floatingcashflows
        price = self.fixedprice if leg == 'Fixed' else self.floatingprice
        duration = 0
        if self.compounding == Compounding.CONTINUOUS:
            for i, cf in enumerate(cashflows):
                duration += self.paymenttimes[i] * cf * self.discountfactors(i) / price
        else:
            k = fi.COMPOUND_MAP.get(self.compounding, None)
            rates = self.yieldcurve.interpolate(self.paymenttimes, 'Spot Rate')
            for i, cf in enumerate(cashflows):
                duration += ((-self.paymenttimes[i] / k) * cf * (1 + rates[i] / k) ** (-self.paymenttimes[i] - 1)) / price
        return duration
    
    def _convexity(self, leg):
        cashflows = self.fixedcashflows if leg == 'Fixed' else self.floatingcashflows
        price = self.fixedprice if leg == 'Fixed' else self.floatingprice
        convexity = 0
        if self.compounding == Compounding.CONTINUOUS:
            for i, cf in enumerate(cashflows):
                convexity += (self.paymenttimes[i] ** 2) * cf * self.discountfactors(i) / price
        else:
            k = fi.COMPOUND_MAP.get(self.compounding, None)
            rates = self.yieldcurve.interpolate(self.paymenttimes, 'Spot Rate')
            for i, cf in enumerate(cashflows):
                convexity += ((self.paymenttimes[i] * (self.paymenttimes[i] + 1)) * (1 / k ** 2) * cf * (1 + rates[i] / k) ** (-self.paymenttimes[i] - 2)) / price
        return convexity
    
    def plot(self, type):
        PLOTSTYLE = {'axes.edgecolor':'#505258', 'grid.linestyle':'dashed', 'grid.color':'white', 'axes.facecolor':'#E8E9EB'}
        sns.set_style('whitegrid', rc = PLOTSTYLE)
        plt.figure(figsize = (12,8))
        sns.barplot(x = self.paymentdates, y = self.fixedvaluationtable[type], color = '#4062BB', label = 'Fixed Leg')
        sns.barplot(x = self.paymentdates, y = -self.floatingvaluationtable[type], color = '#357266', label = 'Floating Leg')
        plt.title(f'{self.region.value} Interest Rate Swap {type} ({self.valuationdate.date()})')
        plt.xlabel('Date')
        plt.ylabel(type)
        plt.grid(True, axis = 'y')
        plt.legend(frameon = False, loc = 'lower center', bbox_to_anchor = (0.5, -0.125), ncol = 2)
        plt.show()