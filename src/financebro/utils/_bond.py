def get_isin_from_cusip(cusip_str, country_code):
    """
    >>> get_isin_from_cusip('037833100', 'US')
    'US0378331005'
    """
    isin_to_digest = country_code + cusip_str.upper()

    get_numerical_code = lambda c: str(ord(c) - 55)
    encode_letters = lambda c: c if c.isdigit() else get_numerical_code(c)
    to_digest = ''.join(map(encode_letters, isin_to_digest))

    ints = [int(s) for s in to_digest[::-1]]
    every_second_doubled = [x * 2 for x in ints[::2]] + ints[1::2]

    sum_digits = lambda i: sum(divmod(i,10))
    digit_sum = sum([sum_digits(i) for i in every_second_doubled])

    check_digit = (10 - digit_sum % 10) % 10
    return isin_to_digest + str(check_digit)


def get_cusip_from_isin(isin_str):
    """
    >>> get_cusip_from_isin('US0378331005')
    '037833100'
    """
    return isin_str[2:-1]


def get_cusip_from_sedol(sedol_str):
    """
    >>> get_cusip_from_sedol('B1YW440')
    'B1YW44'
    """
    return sedol_str[:6]

def get_sedol_from_cusip(cusip_str):
    """
    >>> get_sedol_from_cusip('037833100')
    '037833'
    """
    return cusip_str[:6]

def get_sedol_from_isin(isin_str):
    """
    >>> get_sedol_from_isin('US0378331005')
    '037833'
    """
    return get_sedol_from_cusip(get_cusip_from_isin(isin_str))

def get_isin_from_sedol(sedol_str, country_code):
    """
    >>> get_isin_from_sedol('B1YW44', 'US')
    'USB1YW44'
    """
    return get_isin_from_cusip(get_cusip_from_sedol(sedol_str), country_code)

def get_cusip_from_ticker(ticker_str):
    """
    >>> get_cusip_from_ticker('AAPL')
    '037833100'
    """
    url = f'https://www.marketwatch.com/investing/stock/{ticker_str}/profile'
    resp = requests.get(url)
    if resp.ok:
        soup = BeautifulSoup(resp.text, 'html.parser')
        cusip = soup.find('span', {'class': 'ticker__cusip'}).text
        return cusip
    else:
        raise ValueError(f"Failed to get CUSIP from {url}")
    
def get_ticker_from_cusip(cusip_str):
    """
    >>> get_ticker_from_cusip('037833100')
    'AAPL'
    """
    url = f'https://www.marketwatch.com/investing/stock/{cusip_str}/profile'
    resp = requests.get(url)
    if resp.ok:
        soup = BeautifulSoup(resp.text, 'html.parser')
        ticker = soup.find('span', {'class': 'company__ticker'}).text
        return ticker
    else:
        raise ValueError(f"Failed to get ticker from {url}")
    
def get_ticker_from_isin(isin_str):
    """
    >>> get_ticker_from_isin('US0378331005')
    'AAPL'
    """
    return get_ticker_from_cusip(get_cusip_from_isin(isin_str))

def get_ticker_from_sedol(sedol_str):
    """
    >>> get_ticker_from_sedol('B1YW44')
    'AAPL'
    """
    return get_ticker_from_cusip(get_cusip_from_sedol(sedol_str))

def get_ticker_from_ticker(ticker_str):
    """
    >>> get_ticker_from_ticker('AAPL')
    'AAPL'
    """
    return ticker_str

def get_isin_from_ticker(ticker_str, country_code):
    """
    >>> get_isin_from_ticker('AAPL', 'US')
    'US0378331005'
    """
    return get_isin_from_cusip(get_cusip_from_ticker(ticker_str), country_code)

def get_sedol_from_ticker(ticker_str):
    """
    >>> get_sedol_from_ticker('AAPL')
    'B1YW44'
    """
    return get_sedol_from_cusip(get_cusip_from_ticker(ticker_str))


def compute_price_excel(ytm_percent, rate, N, frequency, redemption, DSC, E):
    # Excel Price computation. WTF is this formula?!
    # See their doc here for notation explanation
    # https://support.microsoft.com/en-us/office/price-function-3ea9deac-8dfa-436f-a7c8-17ea02c21b0a
    yld = ytm_percent/100
    A = E - DSC # number of days from beginning of settlement coupon period to settlement date.
    if N > 1:
        T1: float = redemption / ((1 + yld/frequency) ** (N-1+ DSC/E)) # redemption present value
        T2: float = 0
        for k in range(1, N+1):
            T2 += ( 100*rate/frequency ) / (1 + yld/frequency) ** (k-1+ DSC/E) # sum of the present value of the coupons
        T3 = 100*( rate/frequency ) * (A/E) # minus the interest owed to previous settler
        price_percent = T1 + T2 - T3 # in %
    elif N == 1 : # Only 1 coupon so self.maturity_date == self.next_coupon_date
        # Technically DSR = DSC here but for the sake of readaiblity, I'll five 2 different definitions
        T1 = 100*(rate/frequency) + redemption
        T2 = (yld/frequency)*(DSC/E)  + 1
        T3 = 100*(rate/frequency)*A/E
        price_percent: float = (T1/T2) - T3
    return price_percent


def compute_price_textbook(ytm_percent: float, annual_coupon: float, num_years: int, face_value: float) -> float:
    """
    Compute the approximate price of the bond in percentage of the face value
    From https://www.omnicalculator.com/finance/bond-ytm

    Args:
        ytm_percent (float, optional): Yield to Maturity of the bond in percentage. If None, it uses the ytm of the bond. Defaults to None.
        cash_flows (list): List of cash flows for the bond
        
    Returns:
        float: An approximate price of the bond in percentage
    """        
    # To delete but this should be the true formula from the textbooks... ?!
    # https://www.omnicalculator.com/finance/bond-ytm
    yld = ytm_percent/100
    cash_flows = [annual_coupon]*(num_years-1) + [face_value + annual_coupon]    
    price = 0.
    for i, cf in enumerate(cash_flows):
        price += cf / (1 + yld)**(1+i)
    return price
    