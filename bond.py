

class Bond:
    def __init__(self, facevalue, couponrate, frequency, maturitydate, valuationdate, compounding, region, currency,):	
        self.facevalue = facevalue
        self.couponrate = couponrate
        self.frequency = frequency
        self.maturitydate = maturitydate
        self.valuationdate = valuationdate
        self.compounding = compounding
        self.region = region
        self.currency = currency
        print(self.__repr__())