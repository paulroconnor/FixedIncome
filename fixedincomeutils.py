import pandas as pd
import numpy as np
from datetime import datetime
import pandas_market_calendars as mcal
from enums import Compounding, Region, Calendar, Currency

COMPOUND_MAP = {
    Compounding.WEEKLY: 52,
    Compounding.BIWEEKLY: 26,
    Compounding.MONTHLY: 12,
    Compounding.QUARTERLY: 4,
    Compounding.SEMIANNUAL: 2,
    Compounding.ANNUAL: 1
}

def nelsonsiegelsvensson(time, beta0, beta1, beta2, beta3, lambda0, lambda1):
    t = np.asarray(time, dtype = float)
    with np.errstate(divide = 'ignore', invalid = 'ignore'):
        exp_term0 = np.exp(-t / lambda0)
        exp_term1 = np.exp(-t / lambda1)
        term1 = np.where(t == 0, 1, (1 - exp_term0) / (t / lambda0))
        term2 = term1 - exp_term0
        term3 = np.where(t == 0, 1, (1 - exp_term1) / (t / lambda1)) - exp_term1

    return beta0 + beta1 * term1 + beta2 * term2 + beta3 * term3


def discount(time, rate, compounding):
    time = np.asarray(time, dtype = float)
    if compounding == Compounding.CONTINUOUS:
        return np.exp(-rate * time)
    
    k = COMPOUND_MAP.get(compounding, None)
    if k is None:
        raise ValueError(f'Invalid compounding type: {compounding}')
    return (1 + rate / k) ** (-time * k)
    

def forward(timeA, rateA, timeB, rateB, compounding):
    if timeA >= timeB:
        raise ValueError('timeA must be less than timeB')
    
    if compounding == Compounding.CONTINUOUS:
        return (rateB * timeB - rateA * timeA) / (timeB - timeA)
    
    k = COMPOUND_MAP.get(compounding, None)
    if k is None:
        raise ValueError(f'Invalid compounding type: {compounding}')
    return (k * (((1 + rateB / k) ** timeB) / ((1 + rateA / k) ** timeA)) ** (1 / (timeB - timeA))) - k


def dateschedule(start, end, frequency):
    FREQMAP = {'Weekly':'1W', 'Monthly':'1M', 'Quarterly':'3M', 'Semi-Annual':'6M', 'Annual':'12M'}
    SETDATE = lambda x, d: (datetime.strptime(x.strftime('%Y-%m') + '-' + str(d.day), '%Y-%m-%d')).date()
    period = pd.period_range(start, end, freq = FREQMAP.get(frequency, None))
    period = [SETDATE(x, end) for x in period]
    period = [pd.to_datetime(x) for x in period if pd.to_datetime(x) >= start]
    return period

def businessdayadjust(schedule, calendar):
    cal = mcal.get_calendar(calendar)
    valid = pd.to_datetime(cal.valid_days(start_date = min(schedule), end_date = max(schedule))).tz_localize(None)
    return pd.to_datetime([x if x in valid else valid[valid >= x].min().date() for x in schedule])

def isleapyear(year):
    if (year % 4 == 0):
        return True
    elif (year % 100 == 0) and (year % 400 == 0):
        return True
    else:
        return False

def yearfraction(start, end, convention):
    d1, m1, y1 = [start.day, start.month, start.year]
    d2, m2, y2 = [end.day, end.month, end.year]

    if convention == '30/360':
        return (360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)) / 360

    elif convention == '30U/360':
        if ((m1 == 2) and (d1 in [28, 29])) and ((m2 == 2) and (d2 in [28, 29])):
            d2 = 30
        if (m1 == 2) and (d1 in [28, 29]):
            d1 = 30
        if (d2 == 31) and (d1 in [30, 31]):
            d2 = 30
        if (d1 == 31):
            d1 = 30
        return (360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)) / 360

    elif convention == '30B/360':
        d1 = min(d1, 30)
        if d1 > 29:
            d2 = min(d2, 30)
        if (d2 == 31) and (d1 in [30, 31]):
            d2 = 30
        if (d1 == 31):
            d1 = 30
        return (360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)) / 360

    elif convention == '30E/360':
        if (d1 == 31):
            d1 = 30
        if (d2 == 31):
            d2 = 30
        return (360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)) / 360
    
    elif convention == 'Actual/Actual':
        if y1 == y2:
            if isleapyear(y1):
                return (end - start).days / 366
            else:
                return (end - start).days / 365
        else: 
            if isleapyear(y1):
                dec1 = (datetime(y1, 12, 31) - start).days / 366
            else:
                dec1 = (datetime(y1, 12, 31) - start).days / 365
            
            if isleapyear(y2):
                dec2 = (end - datetime(y2, 1, 1)).days / 366
            else:
                dec2 = (end - datetime(y2, 1, 1)).days / 365
            return dec1 + dec2 + len([year for year in range(y1 + 1, y2)])

    elif convention == 'Actual/365':
        return (end - start).days / 365
    elif convention == 'Actual/360':
        return (end - start).days / 360
    elif convention == 'Actual/364':
        return (end - start).days / 364
    else:
        raise ValueError(f'Invalid day count convention: {convention}')
    
def datetotime(schedule, start, convention):
    return [yearfraction(start, d, convention) for d in schedule]