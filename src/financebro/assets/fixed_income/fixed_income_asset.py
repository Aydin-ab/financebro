import financebro.utils._math as _math
from datetime import date


class FixedIncomeAsset:
    def __init__(self,
                 cusip,
                 isin,
                 price_percent, # in % of face value
                 annual_coupon_rate_percent, # in %
                 coupon_period_days,
                 next_coupon_date,
                 maturity_date,
                 ytm,
                 settlement_date=date.today().strftime("%m-%d-%Y"),
                 face_value= 100, # Let's assume the face value is 100 in the absence of any information
                 date_convention= 'us_nasd_30_360' # 'us_nasd_30_360' or 'not_retarded'
                 ):

        self.cusip = cusip
        self.isin = isin
        self.price_percent = price_percent
        self.annual_coupon_rate_percent = annual_coupon_rate_percent
        self.coupon_period_days = coupon_period_days # in days
        self.next_coupon_date = next_coupon_date
        self.maturity_date = maturity_date # Format 'YYYY-MM-DD'
        self.ytm = ytm
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
        self.coupon_rate_percent = annual_coupon_rate_percent / (360/coupon_period_days)# in %
        self.coupon_rate = self.coupon_rate_percent/100
        self.num_coupons = 1 + _math.day_diff(next_coupon_date, maturity_date, date_convention= date_convention) // coupon_period_days
        
        # Real price to face value
        self.price = price_percent/100 * face_value
        self.face_value_percent = face_value/100


    def compute_return(self):
        pass
    