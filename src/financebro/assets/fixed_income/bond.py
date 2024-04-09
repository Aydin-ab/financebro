from typing import Tuple
import financebro.utils._math as _math
from datetime import date

from financebro.assets.fixed_income.fixed_income_asset import FixedIncomeAsset


class Bond(FixedIncomeAsset):
    """
    A bond is a fixed income instrument that represents a loan made by an investor to a borrower (typically corporate or governmental).

    Args:
        cusip (str): CUSIP number of the bond
        isin (str): ISIN number of the bond
        price_percent (float): Price of the bond in percentage of the face value
        ytm (float): Yield to Maturity of the bond in percentage
        annual_coupon_rate_percent (float): Annual coupon rate of the bond in percentage
        coupon_period_days (int): Number of days between two coupons
        next_coupon_date (str): Next coupon date of the bond in format 'MM-DD-YYYY'
        maturity_date (str): Maturity date of the bond in format 'MM-DD-YYYY'
        settlement_date (str, optional): Settlement date of the bond in format 'MM-DD-YYYY'. Defaults to date.today().strftime("%m-%d-%Y").
        face_value (int, optional): Face value of the bond. Defaults to 1000.
        date_convention (str, optional): Date convention for the bond. Can be 'us_nasd_30_360' | 'not_retarded'. Defaults to 'us_nasd_30_360'.
    """    
    def __init__(self,
                 cusip: str,
                 isin: str,
                 price_percent: float, ytm_percent: float,
                 annual_coupon_rate_percent: float,
                 coupon_period_days: int,
                 maturity_date: str,
                 settlement_date: str= date.today().strftime("%m-%d-%Y"),
                 face_value: int= 1000,
                 date_convention: str= 'us_nasd_30_360'
                 ):

        super().__init__(cusip, isin, 
                         price_percent, ytm_percent, 
                         annual_coupon_rate_percent, coupon_period_days, 
                         maturity_date, settlement_date, 
                         face_value, date_convention)
        self.incomes, self.total_return = self.compute_return()
        self.apy = self.compute_apy()


    def compute_return(self) -> Tuple[float, dict]:
        """
        Compute the total return of the bond and a dict of the incomes date and amount

        Returns:
            float: The total return of the bond
            dict: A dict of the incomes date and amount
        """
        incomes = {}
        for coupon_date in self.coupon_dates:
            incomes[coupon_date] = self.coupon
        incomes[self.maturity_date] += self.face_value

        interest_return = self.num_coupons * self.coupon
        redemption_return = self.face_value - self.price
        total_return = interest_return + redemption_return
        assert total_return == sum(incomes.values())-self.price, f"Total return ({total_return}) and sum of incomes ({sum(incomes.values()) - self.price}) should be equal"
        return incomes, total_return

    def compute_apy(self) -> float:
        """
        Compute the APY of the bond in percentage

        Returns:
            float: The APY of the bond in percentage
        """        
        diff_days = _math.day_diff(self.settlement_date, self.maturity_date)
        _, total_return = self.compute_return()
        yield_percent =  100 *(total_return / self.price)
        daily_yield_percent = yield_percent / diff_days
        apy = daily_yield_percent * self.YEAR_DAYS
        return apy
    
    def compute_ytm(self, price_percent: float= None) -> float:
        """
        Compute the Yield to Maturity of the bond in percentage
        From https://support.microsoft.com/en-gb/office/yield-function-f5f5ca43-c4bd-434f-8bd2-ed3c9727a4fe

        Args:
            price (float, optional): Price in percentage of the face value. If None it uses the price of the bond. Defaults to None.

        Returns:
            float: The Yield to Maturity of the bond in percentage
        """        
        # Excel YTM computation
        if price_percent is None:
            price_percent = self.price_percent
        def f(x):
            approx_price_percent = self.compute_price(x)
            diff = approx_price_percent - price_percent
            return diff
        ytm: float = _math.solve_newton(f, 5)
        return ytm
    
    def compute_approx_ytm(self, price_percent: float= None) -> float:
        """
        Compute the approximate Yield to Maturity of the bond in percentage
        From https://www.wallstreetprep.com/knowledge/yield-to-maturity-ytm/

        Args:
            price (float, optional): Price in percentage of the face value. If None it uses the price of the bond. Defaults to None.

        Returns:
            float: An approximate Yield to Maturity of the bond in percentage
        """        
        # Formula here
        # https://www.wallstreetprep.com/knowledge/yield-to-maturity-ytm/
        price = self.price if price_percent is None else price_percent/100 * self.face_value
        total_interest = self.num_coupons * self.coupon_rate * self.face_value
        days_to_maturity = _math.day_diff(self.settlement_date, self.maturity_date)
        interest_per_day = total_interest / days_to_maturity
        interest_per_year = interest_per_day * self.YEAR_DAYS
        num_years = days_to_maturity / self.YEAR_DAYS

        approx_ytm = interest_per_year + (self.face_value - price) / num_years
        approx_ytm = approx_ytm/ ((price + self.face_value)/2)
        approx_ytm = approx_ytm * 100
        return approx_ytm
    
    def compute_price(self, ytm_percent: float= None) -> float:
        """
        Compute the price of the bond in percentage of the face value
        From https://support.microsoft.com/en-us/office/price-function-3ea9deac-8dfa-436f-a7c8-17ea02c21b0a

        Args:
            ytm_percent (float, optional): Yield to Maturity of the bond in percentage. If None, it uses the ytm of the bond. Defaults to None.

        Returns:
            float: The price of the bond in percentage of the face value
        """
        # Excel Price computation. WTF is this formula?!
        # See their doc here for notation explanation
        # https://support.microsoft.com/en-us/office/price-function-3ea9deac-8dfa-436f-a7c8-17ea02c21b0a
        if ytm_percent is None:
            ytm_percent = self.ytm_percent
        
        # Excel Notation for the formula
        N = self.num_coupons
        E = self.coupon_period_days # number of days in the coupon period
        frequency = self.YEAR_DAYS / self.coupon_period_days
        redemption = 100 # standardized at 100, not 1000
        yld = ytm_percent/100
        rate = self.annual_coupon_rate_percent/100
        next_coupon_date = self.coupon_dates[0]
        if N > 1:
            DSC = _math.day_diff(self.settlement_date, next_coupon_date) # number of days from settlement to next coupon date. DSC = DSR if N = 1
            A = E - DSC # number of days from beginning of settlement coupon period to settlement date.
            T1: float = redemption / ((1 + yld/frequency) ** (N-1+ DSC/E)) # redemption present value
            T2: float = 0
            for k in range(1, N+1):
                T2 += ( 100*rate/frequency ) / (1 + yld/frequency) ** (k-1+ DSC/E) # sum of the present value of the coupons
            T3 = 100*( rate/frequency ) * (A/E) # minus the interest owed to previous settler
            price_percent = T1 + T2 - T3 # in %
        elif N == 1 : # Only 1 coupon so self.maturity_date == self.next_coupon_date
            # Technically DSR = DSC here but for the sake of readaiblity, I'll five 2 different definitions
            DSR = _math.day_diff(self.settlement_date, self.maturity_date) # number of days from settlement to redemption date.
            A = E - DSR # number of days from beginning of settlement coupon period to settlement date.
            T1 = 100*(rate/frequency) + redemption
            T2 = (yld/frequency)*(DSR/E)  + 1
            T3 = 100*(rate/frequency)*A/E
            price_percent: float = (T1/T2) - T3
        
        return price_percent
    
    def compute_approx_price(self, ytm_percent: float= None) -> float:
        """
        Compute the approximate price of the bond in percentage of the face value
        From https://www.omnicalculator.com/finance/bond-ytm

        Args:
            ytm_percent (float, optional): Yield to Maturity of the bond in percentage. If None, it uses the ytm of the bond. Defaults to None.

        Returns:
            float: An approximate price of the bond in percentage
        """        
        # To delete but this should be the true formula from the textbooks... ?!
        # https://www.omnicalculator.com/finance/bond-ytm
        ytm = self.ytm if ytm_percent is None else ytm_percent/100
        annual_coupon_cash_flow = self.annual_coupon_rate * self.face_value
        days_to_maturity = _math.day_diff(self.settlement_date, self.maturity_date)
        num_years = days_to_maturity // self.YEAR_DAYS

        cash_flows = [annual_coupon_cash_flow]*(num_years-1) + [self.face_value + annual_coupon_cash_flow]
        price = 0.
        for i, cf in enumerate(cash_flows):
            price += cf / (1 + ytm)**(1+i)
        return price
    

# TODO To simplify for now, consider worst case which is CallableBond are called on first day of call date
class CallableBond(Bond):
    def __init__(self,
                 cusip,
                 isin,
                 price_percent, ytm_percent,
                 annual_coupon_rate_percent,
                 coupon_period_days,
                 call_date, # Same as maturity date if not callable
                 settlement_date=date.today().strftime("%m-%d-%Y"),
                 face_value= 1000,
                 date_convention= 'us_nasd_30_360'
                 ):
        super().__init__(cusip, isin, 
                         price_percent, ytm_percent, 
                         annual_coupon_rate_percent, coupon_period_days, 
                         call_date, settlement_date,
                         face_value, date_convention)
