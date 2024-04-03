import financebro.utils._math as _math
from datetime import date

from financebro.assets.fixed_income.fixed_income_asset import FixedIncomeAsset


class Bond(FixedIncomeAsset):
    def __init__(self,
                 cusip,
                 isin,
                 price_percent,
                 annual_coupon_rate_percent,
                 coupon_period_days,
                 next_coupon_date,# TODO can actually be inferred from the settlement date, the coupon period and the maturity date
                 maturity_date,
                 ytm,
                 settlement_date=date.today().strftime("%m-%d-%Y"),
                 face_value= 1000,
                 date_convention= 'us_nasd_30_360'
                 ):

        super().__init__(cusip, isin, price_percent, annual_coupon_rate_percent, coupon_period_days, next_coupon_date, maturity_date, ytm, settlement_date, face_value, date_convention)
        self.ytm = ytm
        self.total_return = self.compute_return()
        self.apy = self.compute_apy()


    def compute_return(self):
        interest_return = self.num_coupons * self.coupon_rate * self.face_value
        redemption_return = self.face_value - self.price
        total_return = interest_return + redemption_return
        return total_return

    def compute_apy(self):
        diff_days = _math.day_diff(self.settlement_date, self.maturity_date)
        total_return = self.compute_return()
        yield_percent =  100 *(total_return / self.price)
        daily_yield_percent = yield_percent / diff_days
        apy = daily_yield_percent * self.YEAR_DAYS
        return apy
    
    def compute_ytm(self, price= None):
        # Excel YTM computation
        # https://support.microsoft.com/en-gb/office/yield-function-f5f5ca43-c4bd-434f-8bd2-ed3c9727a4fe
        if price is None:
            price = self.price
        def f(x):
            approx_price = self.compute_price(x)
            return approx_price - self.price
        ytm = _math.solve_newton(f, 5)
        return ytm
    
    def compute_approx_ytm(self, price= None):
        # Formula here
        # https://www.wallstreetprep.com/knowledge/yield-to-maturity-ytm/
        if price is None:
            price = self.price
        total_interest = self.num_coupons * self.coupon_rate * self.face_value
        days_to_maturity = _math.day_diff(self.settlement_date, self.maturity_date)
        interest_per_day = total_interest / days_to_maturity
        interest_per_year = interest_per_day * self.YEAR_DAYS
        num_years = days_to_maturity / self.YEAR_DAYS

        approx_ytm = interest_per_year + (self.face_value - self.price) / num_years
        approx_ytm = approx_ytm/ ((self.price + self.face_value)/2)
        approx_ytm = approx_ytm * 100
        return approx_ytm
    
    def compute_price(self, ytm= None):
        # Excel Price computation. WTF is this formula?!
        # See their doc here for notation explanation
        # https://support.microsoft.com/en-us/office/price-function-3ea9deac-8dfa-436f-a7c8-17ea02c21b0a
        if ytm is None:
            ytm = self.ytm
        
        # Excel Notation for the formula
        dsc = _math.day_diff(self.settlement_date, self.next_coupon_date)
        E = self.coupon_period_days
        frequency = self.YEAR_DAYS / self.coupon_period_days
        redemption = 100 # standardized at 100, not 1000
        yld = ytm/100
        rate = self.annual_coupon_rate_percent/100
        N = self.num_coupons
        A = E - dsc

        T1 = redemption / ((1 + yld/frequency) ** (N-1+ dsc/E)) # fuck u excel
        T2 = 0
        for k in range(1, N+1):
            T2 += ( 100*rate/frequency ) / (1 + yld/frequency) ** (k-1+ dsc/E) #wtf
        T3 = 100*( rate/frequency ) * (A/E) # bitch ass non sense
        price_percent = T1 + T2 - T3 # in %
        price = (price_percent/100)*self.face_value
        return price
    
    def compute_approx_price(self, ytm= None):
        # To delete but this should be the true formula from the textbooks... ?!
        # https://www.omnicalculator.com/finance/bond-ytm
        if ytm is None:
            ytm = self.ytm
        ytm_percent = ytm/100
        annual_coupon_cash_flow = self.annual_coupon_rate * self.face_value
        days_to_maturity = _math.day_diff(self.settlement_date, self.maturity_date)
        num_years = days_to_maturity // self.YEAR_DAYS

        cash_flows = [annual_coupon_cash_flow]*(num_years-1) + [self.face_value + annual_coupon_cash_flow]
        price = 0
        for i, cf in enumerate(cash_flows):
            price += cf / (1 + ytm_percent)**(1+i)
        return price
    

# TODO To simplify for now, consider worst case which is CallableBond are called on first day of call date
class CallableBond(Bond):
    def __init__(self,
                 cusip,
                 isin,
                 price_percent,
                 annual_coupon_rate_percent,
                 coupon_period_days,
                 next_coupon_date,# TODO can actually be inferred from the settlement date, the coupon period and the maturity date
                 call_date, # Same as maturity date if not callable
                 ytm,
                 settlement_date=date.today().strftime("%m-%d-%Y"),
                 face_value= 1000,
                 date_convention= 'us_nasd_30_360'
                 ):
        super().__init__(cusip, isin, price_percent, annual_coupon_rate_percent, coupon_period_days, next_coupon_date, call_date, ytm, settlement_date, face_value, date_convention)
