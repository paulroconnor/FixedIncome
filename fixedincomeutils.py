import pandas as pd
import numpy as np
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


def discount(time, rate, compounding = Compounding.CONTINUOUS):
    if compounding == Compounding.CONTINUOUS:
        return np.exp(-rate * time)
    
    k = COMPOUND_MAP.get(compounding, None)
    if k is None:
        raise ValueError(f'Invalid compounding type: {compounding}')
    return (1 + rate / k) ** (-time * k)
    

def forward(timeA, rateA, timeB, rateB, compounding = Compounding.CONTINUOUS):
    if timeA >= timeB:
        raise ValueError('timeA must be less than timeB')
    
    if compounding == Compounding.CONTINUOUS:
        return (rateB * timeB - rateA * timeA) / (timeB - timeA)
    
    k = COMPOUND_MAP.get(compounding, None)
    if k is None:
        raise ValueError(f'Invalid compounding type: {compounding}')
    return (k * (((1 + rateB / k) ** timeB) / ((1 + rateA / k) ** timeA)) ** (1 / (timeB - timeA))) - k