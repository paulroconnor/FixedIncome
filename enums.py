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
    SPOT = 'Spot Rate'
    DISCOUNT = 'Discount Factor'
    FORWARD = 'Forward Rate'

class Calendar(Enum):
    US = 'SIFMAUS'
    UK = 'SIFMAUK'
    JP = 'SIFMAJP'
    EU = 'EUREX_Bond'

class Frequency(Enum):
    WEEKLY = 'Weekly'
    MONTHLY = 'Monthly'
    QUARTERLY = 'Quarterly'
    SEMIANNUAL = 'Semi-Annual'
    ANNUAL = 'Annual'

class Convention(Enum):
    DC30360 = '30/360'
    DC30U360 = '30U/360'
    DC30E360 = '30E/360'
    DC30B360 = '30B/360'
    DCACTACT = 'Actual/Actual'
    DCACT365 = 'Actual/365'
    DCACT364 = 'Actual/364'
    DCACT360 = 'Actual/360'