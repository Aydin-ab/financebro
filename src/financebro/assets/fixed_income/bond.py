from typing import Tuple
from datetime import date

from financebro.assets.fixed_income.fixed_income_asset import FixedIncomeAsset
import financebro.utils._math as _math
import financebro.utils._bond as _bond


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
                 price_percent: float, ytm_percent: float,
                 annual_coupon_rate_percent: float,
                 maturity_date: str,
                 coupon_period_days: int= None,
                 settlement_date: str= date.today().strftime("%m/%d/%Y"),
                 face_value: int= 1000,
                 date_convention: str= 'us_nasd_30_360'
                 ):
        super().__init__(price_percent, ytm_percent, 
                         annual_coupon_rate_percent, 
                         maturity_date, settlement_date, 
                         face_value, date_convention)
        self.cusip = cusip
        self.isin = _bond.get_isin_from_cusip(cusip, 'US')

        # Couponing
        if coupon_period_days is None:
            self.coupon_dates, self.coupon_period_days = self.infer_coupons_dates()
        else:
            self.coupon_period_days = coupon_period_days
            self.coupon_dates = _bond.get_coupons_date(settlement_date, maturity_date, coupon_period_days, date_convention)
        self.num_coupons_per_year = (360/self.coupon_period_days) if date_convention == 'us_nasd_30_360' else (365/self.coupon_period_days)
        self.coupon_rate_percent = annual_coupon_rate_percent / self.num_coupons_per_year# in %
        self.coupon_rate = self.coupon_rate_percent/100
        self.coupon = self.coupon_rate * face_value
        self.num_coupons = len(self.coupon_dates)

        
        self.incomes, self.total_return = self.compute_return()
        self.apy = self.compute_apy()

    def compute_return(self) -> Tuple[dict, float]:
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
        assert round(total_return, 3) == round(sum(incomes.values())-self.price, 3), f"Total return ({total_return}) and sum of incomes ({sum(incomes.values()) - self.price}) should be equal"
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
    
    def compute_ytm_percent(self, price_percent: float= None) -> float:
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
        if self.num_coupons > 1:
            def f(x):
                approx_price_percent = self.compute_price(x)
                diff = approx_price_percent - price_percent
                return diff
            ytm_percent: float = _math.solve_newton(f, 5)
        elif self.num_coupons == 1:
            ytm_percent = _bond.compute_ytm_excel_1_coupon(price_percent,
                                                    self.annual_coupon_rate,
                                                    self.num_coupons_per_year,
                                                    self.face_value_percent,
                                                    _math.day_diff(self.settlement_date, self.coupon_dates[0]),
                                                    self.coupon_period_days)
        return ytm_percent
    
    def compute_approx_ytm_percent(self, price_percent: float= None) -> float:
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
    
    def compute_price(self, ytm_percent: float= None, method: str= 'excel') -> float:
        """
        Compute the price of the bond in percentage of the face value
        From https://support.microsoft.com/en-us/office/price-function-3ea9deac-8dfa-436f-a7c8-17ea02c21b0a

        Args:
            ytm_percent (float, optional): Yield to Maturity of the bond in percentage. If None, it uses the ytm of the bond. Defaults to None.
            method (str, optional): Method to use to compute the price. Can be 'excel' or 'textbook'. Defaults to 'excel'.
            
        Returns:
            float: The price of the bond in percentage of the face value
        """
        if ytm_percent is None:
            ytm_percent = self.ytm_percent
        
        if method == 'excel':
            # Excel Notation for the formula
            DSC = _math.day_diff(self.settlement_date, self.coupon_dates[0])
            price_percent = _bond.compute_price_excel(ytm_percent, 
                                                    self.annual_coupon_rate, 
                                                    self.num_coupons, 
                                                    self.num_coupons_per_year, 
                                                    self.face_value_percent, 
                                                    DSC, 
                                                    self.coupon_period_days)        
        elif method == 'textbook':
            # Textbook Notation for the formula
            days_to_maturity = _math.day_diff(self.settlement_date, self.maturity_date)
            num_years = days_to_maturity // self.YEAR_DAYS
            price_percent = _bond.compute_price_textbook(ytm_percent, 
                                                        self.annual_coupon, 
                                                        num_years, 
                                                        self.face_value)
        
        return price_percent

    def infer_coupons_dates(self) -> Tuple[list, int]:
        """
        Infer the number of coupons of the bond from the price computation

        Args:
            ytm_percent (float): Yield to Maturity of the bond in percentage

        Returns:
            int: The number of coupons of the bond
        """
        trials = [15, 30, 60, 90, 120, 180, 360]
        found = False
        log_tried = []
        for trial in trials:
            coupon_dates = _bond.get_coupons_date(self.settlement_date, self.maturity_date, trial, self.date_convention)
            DSC = _math.day_diff(self.settlement_date, coupon_dates[0])
            num_coupons_per_year = (360/trial)
            price_percent = _bond.compute_price_excel(self.ytm_percent,
                                                      self.annual_coupon_rate, 
                                                      len(coupon_dates), 
                                                      num_coupons_per_year, 
                                                      self.face_value_percent, 
                                                      DSC, 
                                                      trial)
            log_tried.append((trial, price_percent))
            if abs(round(price_percent, 3) - self.price_percent) < 0.01:
                found = True
                break
        if found:
            return coupon_dates, trial
        else:
            raise ValueError("Could not infer the number of coupons of the bond")



# TODO To simplify for now, consider worst case which is CallableBond are called on first day of call date
class CallableBond(Bond):
    def __init__(self,
                 cusip: str,
                 price_percent:float , ytm_percent: float,
                 annual_coupon_rate_percent: float,
                 call_date: str, # Same as maturity date if not callable
                 coupon_period_days:int = None,
                 settlement_date=date.today().strftime("%m-%d-%Y"),
                 face_value: float= 1000,
                 date_convention: str= 'us_nasd_30_360'
                 ):
        super().__init__(cusip, 
                         price_percent, ytm_percent, 
                         annual_coupon_rate_percent, coupon_period_days, 
                         call_date, settlement_date,
                         face_value, date_convention)
