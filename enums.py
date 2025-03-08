from enum import Enum

class Compounding(Enum):
    CONTINUOUS = 'Continuous'
    WEEKLY = 'Weekly'
    BIWEEKLY = 'Bi-Weekly'
    MONTHLY = 'Monthly'
    QUARTERLY = 'Quarterly'
    SEMIANNUAL = 'Semi-Annual'
    ANNUAL = 'Annual'

class Region(Enum):
    US = 'United States'
    EU = 'European Union'
    JP = 'Japan'
    CN = 'China'
    GB = 'United Kingdom'
    CA = 'Canada'

class Currency(Enum):
    USD = 'United States Dollar'
    EUR = 'Euro'
    JPY = 'Japanese Yen'
    CNY = 'Chinese Yuan'
    GBP = 'British Pound'
    CAD = 'Canadian Dollar'

class InterpolationType(Enum):
    SPOT = 'Spot'
    DISCOUNT = 'Discount'
    FORWARD = 'Forward'