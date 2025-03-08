# from yieldcurve import YieldCurve
from enums import Compounding, Region, Currency, Calendar
from validation import validate_enum, default_calendar, default_currency, validate_date

class Bond:
    def __init__(self, facevalue, couponrate, frequency, maturitydate, valuationdate, compounding, region, currency = None, calendar = None):	
        self.facevalue = facevalue
        self.couponrate = couponrate
        self.frequency = frequency
        self.region = validate_enum(region, Region, 'region')
        self.currency = validate_enum(currency, Currency, 'currency') if currency else default_currency(self.region)
        self.calendar = validate_enum(calendar, Calendar, 'calendar') if calendar else default_calendar(self.region)
        self.compounding = validate_enum(compounding, Compounding, 'compounding')
        self.maturitydate = validate_date(maturitydate, self.calendar)
        self.valuationdate = validate_date(valuationdate, self.calendar)
        print(self.__repr__())

    def __repr__(self):
        return f'Bond(facevalue = {self.facevalue:,}, couponrate = {self.couponrate :.2%}, frequency = {self.frequency}, maturitydate = {self.maturitydate.date()}, valuationdate = {self.valuationdate.date()}, region = {self.region.value}, currency = {self.currency.value}, compounding = {self.compounding.value})'
        
b = Bond(1000, 0.05, 2, '2025-01-13', '2021-12-31', 'Semi-Annual', 'United States')