import pandas as pd
import pandas_market_calendars as mcal
from enums import Compounding, Region, Calendar, Currency


def validate_enum(value, enum_class, name):
    try:
        return enum_class(value) if isinstance(value, str) else value
    except ValueError:
        valid_values = ', '.join(e.value for e in enum_class)
        raise ValueError(f'Invalid {name}: {value}. Choose from {valid_values}')
    

def validate_date(date_str, calendar: Calendar):
    try:
        date = pd.to_datetime(date_str)
    except ValueError:
        raise ValueError(f'Invalid date: {date_str}. Use format YYYY-MM-DD')
    
    cal = mcal.get_calendar(calendar.value)
    if not cal.valid_days(start_date = date, end_date = date).size:
        raise ValueError(f'Invalid date: {date_str}. Not a valid trading day. Next valid date is {cal.valid_days(start_date = date, end_date = date + pd.DateOffset(days = 14)).min()}')
    return date

def default_calendar(region: Region):
    CALENDARMAP = {
        Region.US: Calendar.US,
        Region.EU: Calendar.EU,
        Region.JP: Calendar.JP,
        Region.UK: Calendar.UK
        # Region.CA: Calendar.CA
        # Region.CN: Calendar.CN
    }
    return CALENDARMAP.get(region, None)


def default_currency(region: Region):
    CURRENCYMAP = {
        Region.US: Currency.USD,
        Region.EU: Currency.EUR,
        Region.JP: Currency.JPY,
        Region.UK: Currency.GBP
        # Region.CA = Currency.CAD
        # Region.CN = Currency.CNY
    }
    return CURRENCYMAP.get(region, None)