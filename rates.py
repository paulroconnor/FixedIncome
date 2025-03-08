import numpy as np
import warnings

def nelsonsiegelsvensson(time, beta0, beta1, beta2, beta3, lambda0, lambda1):
    # beta0: Long-Term Level of Yields
    # beta1: Short-Term Component
    # beta2: Medium-Term Hump or Curvature
    # beta3: Extra Flexibility for Long-Term Component
    # lambda0: Decay Factor for beta1 and beta2
    # lambda1: Decay Factor for beta3
    
    t = np.asarray(time, dtype = float)

    warnings.simplefilter('ignore', category = RuntimeWarning)
    term1 = (1 - np.exp(-t / lambda0)) / (t / lambda0)
    term2 = term1 - np.exp(-t / lambda0)
    term3 = (1 - np.exp(-t / lambda1)) / (t / lambda1) - np.exp(-t / lambda1)
    warnings.simplefilter('default', category = RuntimeWarning)

    return beta0 + beta1 * term1 + beta2 * term2 + beta3 * term3

def discount(time, rate, compounding = 'continuous'):
    if compounding == 'continuous':
        return np.exp(-rate * time)
    else:
        COMPOUNDMAP = {'Monthly':1,'Quarterly':4,'Semi-Annual':2,'Annual':1}
        return (1 + rate / COMPOUNDMAP[compounding]) ** (-time * COMPOUNDMAP[compounding])
    
def forward(timeA, rateA, timeB, rateB, compounding = 'continuous'):
    if timeA >= timeB:
        raise ValueError('timeA must be less than timeB')
    
    if compounding == 'continuous':
        return (rateB * timeB - rateA * timeA) / (timeB - timeA)
    else:
        COMPOUNDMAP = {'Monthly':1,'Quarterly':4,'Semi-Annual':2,'Annual':1}
        k = COMPOUNDMAP[compounding]
        return (k * (((1 + rateB / k) ** timeB) / ((1 + rateA / k) ** timeA)) ** (1 / (timeB - timeA))) - k