import financebro.utils._math as _math
from datetime import date, datetime, timedelta

class FixedIncomeAsset:
    def __init__(self,
                 price_percent: float, # in % of face value
                 ytm_percent: float,
                 annual_coupon_rate_percent: float, # in %
                 coupon_period_days: int,
                 maturity_date: str,
                 settlement_date: str= date.today().strftime("%m-%d-%Y"),
                 face_value: float= 1000, # Let's assume the face value is 1000 in the absence of any information
                 date_convention: str= 'us_nasd_30_360' # 'us_nasd_30_360' or 'not_retarded'
                 ):

        self.price_percent = price_percent
        self.annual_coupon_rate_percent = annual_coupon_rate_percent
        self.coupon_period_days = coupon_period_days # in days
        self.maturity_date = maturity_date # Format 'YYYY-MM-DD'
        self.ytm_percent = ytm_percent
        self.settlement_date = settlement_date
        self.face_value = face_value
        self.date_convention = date_convention

        # Compute some other values
        if date_convention == 'us_nasd_30_360':
            self.YEAR_DAYS = 360 # middle age convention
        elif date_convention == 'not_retarded':
            self.YEAR_DAYS = 365
        else:
            raise ValueError(f"Convention implemented : 'us_nasd_30_360' and 'not_retarded' but got {date_convention}")
        
        # Couponing
        self.annual_coupon_rate = self.annual_coupon_rate_percent/100
        self.annual_coupon = self.annual_coupon_rate * face_value
        self.num_coupons_per_year = (360/coupon_period_days) if date_convention == 'us_nasd_30_360' else (365/coupon_period_days)
        self.coupon_rate_percent = annual_coupon_rate_percent / self.num_coupons_per_year# in %
        self.coupon_rate = self.coupon_rate_percent/100
        self.coupon = self.coupon_rate * face_value
        iter_date = maturity_date
        self.coupon_dates = []
        while datetime.strptime(iter_date, "%m-%d-%Y") >= datetime.strptime(settlement_date, "%m-%d-%Y"):
            self.coupon_dates.insert(0, iter_date)
            iter_date = _math.remove_days(iter_date, coupon_period_days, date_convention)
        self.num_coupons = len(self.coupon_dates)

        # Real price to face value
        self.price = price_percent/100 * face_value
        self.ytm = self.ytm_percent/100
        self.face_value_percent = 100 # by definition



    def compute_return(self):
        pass
    