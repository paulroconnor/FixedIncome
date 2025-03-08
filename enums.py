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
    UK = 'United Kingdom'
    # CA = 'Canada'
    # CN = 'China'

class Currency(Enum):
    USD = 'United States Dollar'
    EUR = 'Euro'
    JPY = 'Japanese Yen'
    GBP = 'British Pound'
    # CNY = 'Chinese Yuan'
    # CAD = 'Canadian Dollar'

class InterpolationType(Enum):
    SPOT = 'Spot'
    DISCOUNT = 'Discount'
    FORWARD = 'Forward'

class Calendar(Enum):
    US = 'SIFMAUS'
    UK = 'SIFMAUK'
    JP = 'SIFMAJP'
    EU = 'EUREX_Bond'