import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from yieldcurve import YieldCurve
from enums import Compounding, Region, Currency, Calendar, Frequency, Convention
import validation as v
import fixedincomeutils as fi

class Bond:
    def __init__(self, facevalue, couponrate, frequency, maturitydate, valuationdate, compounding, convention, region, currency = None, calendar = None):	
        self.facevalue = facevalue
        self.couponrate = couponrate
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
        self.cashflows = self._cashflows()
        self.yieldcurve = YieldCurve(self.region, self.valuationdate, self.compounding, self.currency, self.calendar)
        self.discountfactors = self._discountfactors()
        self.price = self._price()
        self.valuationtable = self._valuationtable()

    def __repr__(self):
        return f'Bond(facevalue = {self.facevalue:,}, couponrate = {self.couponrate :.2%}, frequency = {self.frequency.value}, maturitydate = {self.maturitydate.date()}, valuationdate = {self.valuationdate.date()}, region = {self.region.value}, currency = {self.currency.value}, compounding = {self.compounding.value}, calendar = {self.calendar.value}, convention = {self.convention.value})'
    
    def _paymentdates(self):
        dates = fi.dateschedule(self.valuationdate, self.maturitydate, self.frequency.value)
        return fi.businessdayadjust(dates, self.calendar.value)

    def _paymenttimes(self):
        return fi.datetotime(self.paymentdates, self.valuationdate, self.convention.value)

    def _cashflows(self):
        FREQMAP = {'Weekly':52, 'Monthly':12, 'Quarterly':4, 'Semi-Annual':2, 'Annual':1}
        cashflows = [self.facevalue * self.couponrate / FREQMAP.get(self.frequency.value, None)] * len(self.paymentdates)
        cashflows[-1] += self.facevalue
        return cashflows

    def _discountfactors(self):
        return self.yieldcurve.interpolate(self.paymenttimes, 'Discount Factor')

    def _price(self):
        cashflows = np.asarray(self.cashflows, dtype = float)
        discountfactors = np.asarray(self.discountfactors, dtype = float)
        return cashflows @ discountfactors

    def _valuationtable(self):
        return pd.DataFrame({
            'Payment Date': self.paymentdates,
            'Time': self.paymenttimes,
            'Cash Flow': self.cashflows,
            'Discount Factor': self.discountfactors,
            'Present Value': self.cashflows * self.discountfactors
        })
    
    def plot(self, type):
        PLOTSTYLE = {'axes.edgecolor':'#505258', 'grid.linestyle':'dashed', 'grid.color':'white', 'axes.facecolor':'#E8E9EB'}
        sns.set_style('whitegrid', rc = PLOTSTYLE)
        plt.figure(figsize = (12,8))
        sns.barplot(x = self.paymentdates, y = self.valuationtable[type], color = '#4062BB')
        plt.title(f'{self.region.value} Bond {type} ({self.valuationdate.date()})')
        plt.xlabel('Date')
        plt.ylabel(type)
        plt.grid(True, axis = 'y')
        plt.show()
        
        
# b = Bond(facevalue = 100, couponrate = 0.25, frequency = 'Monthly', maturitydate = '2025-01-13', valuationdate = '2024-06-18', compounding = 'Semi-Annual', convention = 'Actual/Actual', region = 'United States')
# # print(b.price)
# # print(b.valuationtable)
# b.plot(type = 'Present Value')