import datetime
import calendar
import scipy.optimize as optimize
from typing import Callable


def day_diff(start_time: str, end_time: str, date_convention: str= 'us_nasd_30_360') -> int:
    """
    Compute the difference in days between two dates

    Args:
        start_time (str): Start date in format 'MM/DD/YYYY'
        end_time (str): End date in format 'MM/DD/YYYY'
        date_convention (str, optional): Calendar convention.  Can be 'us_nasd_30_360' | 'not_retarded'. Defaults to 'us_nasd_30_360'.

    Raises:
        ValueError: Invalid date convention mode

    Returns:
        int: Difference in days between the two dates
    """    
    if date_convention == 'not_retarded':
        diff = day_diff_normal(start_time, end_time)
    elif date_convention == 'us_nasd_30_360':
        diff = day_diff_us_nasd_30_360(start_time, end_time, excel= True)
    else:
        raise ValueError(f"Invalid mode: {date_convention}")
    return diff

def day_diff_normal(start_time: str, end_time: str) -> int:
    """
    Compute the difference in days between two dates using the normal calendar convention

    Args:
        start_time (str): Start date in format 'MM/DD/YYYY'
        end_time (str): End date in format 'MM/DD/YYYY'

    Returns:
        int: Difference in days between the two dates
    """    
    # Convert string of format MM/DD/YYYY to datetime object
    start_time = datetime.datetime.strptime(start_time, "%m/%d/%Y")
    end_time = datetime.datetime.strptime(end_time, "%m/%d/%Y")
    diff = end_time - start_time
    days = diff.days
    return days

def day_diff_us_nasd_30_360(start_time: str, end_time: str, excel: bool= True) -> int:
    """
    Compute the difference in days between two dates using the US NASD 30/360 calendar convention
    If excel is set to True, the function will use the Excel function DAYS360 output which I found to be different from the actual 30/360 convention. (bug)
    The Excel function DAYS360 seems to forget the rule that the last day of February is the 30th day of February.

    Args:
        start_time (str): Start date in format 'MM/DD/YYYY'
        end_time (str): End date in format 'MM/DD/YYYY'
        excel (bool, optional): Use Excel function DAYS360 output. Defaults to True.

    Returns:
        int: Difference in days between the two dates
    """    
    # https://sqlsunday.com/2014/08/17/30-360-day-count-convention/ 
    # Convert string of format MM/DD/YYYY to datetime object
    start_time = datetime.datetime.strptime(start_time, "%m/%d/%Y")
    end_time = datetime.datetime.strptime(end_time, "%m/%d/%Y")
    start_day = start_time.day
    start_month = start_time.month
    end_day = end_time.day
    end_month = end_time.month
    if start_month == 2 and start_day == calendar.monthrange(start_time.year, start_month)[1]:
        start_day = 30
        if not excel and end_day == calendar.monthrange(end_time.year, end_month)[1]:
        # Excel seems to forget that rule...
        # Try ('02/29/2024', '02/29/2024') or ('02/29/2024', '02/28/2025') they should return 0 and 360 respectively but here it doesn't..
        # That condition here fixes it
            end_day = 30
    if start_day == 31:
        start_day = 30
    if end_day == 31 and start_day == 30:
        end_day = 30
    days = 360 * (end_time.year - start_time.year) + 30 * (end_month - start_month) + (end_day - start_day)
    return days


def remove_days(time: str, days: int, date_convention: str= 'us_nasd_30_360') -> str:
    """
    Remove days from a date given a calendar convention

    Args:
        time (str): Date in format 'MM/DD/YYYY'
        days (int): Number of days to remove
        date_convention (str, optional): Calendar convention. Can be 'us_nasd_30_360' | 'not_retarded'. Defaults to 'us_nasd_30_360'.

    Returns:
        str: Date in format 'MM/DD/YYYY'
    """    
    if date_convention == 'not_retarded':
        new_date = remove_days_normal(time, days)
    elif date_convention == 'us_nasd_30_360':
        new_date = remove_days_us_nasd_30_360(time, days)
    else:
        raise ValueError(f"Invalid mode: {date_convention}")
    return new_date

def remove_days_normal(time: str, days: int) -> str:
    """
    Remove days from a date using the normal calendar convention

    Args:
        time (str): Date in format 'MM/DD/YYYY'
        days (int): Number of days to remove

    Returns:
        str: Date in format 'MM/DD/YYYY'
    """    
    dtime = datetime.datetime.strptime(time, "%m/%d/%Y")
    dtime = dtime - datetime.timedelta(days= days)
    dtime = dtime.strftime("%m/%d/%Y")
    return dtime

def remove_days_us_nasd_30_360(time: str, days: int) -> str:
    """
    Remove days from a date using the US NASD 30/360 calendar convention

    Args:
        time (str): Date in format 'MM/DD/YYYY'
        days (int): Number of days to remove

    Returns:
        str: Date in format 'MM/DD/YYYY'
    """    
    dtime = datetime.datetime.strptime(time, "%m/%d/%Y")
    num_years = days // 360
    num_months = (days % 360) // 30
    num_days = (days % 360) % 30
    new_year = dtime.year - num_years
    new_month = dtime.month - num_months
    new_day = dtime.day - num_days
    if new_day <= 0:
        new_month -= 1
        new_day += 30
    if new_month <= 0:
        new_month += 12
        new_year -= 1
    dtime = datetime.datetime(new_year, new_month, new_day)
    dtime = dtime.strftime("%m/%d/%Y")
    return dtime

def solve_newton(f: Callable, x0: float, tol: float=1e-10, max_iter: int=100):
    """
    Solve the equation f(x) = 0 using the Newton method

    Args:
        f (function): The function to solve
        x0 (float): Initial guess
        tol (float, optional): Idk. Defaults to 1e-10.
        max_iter (int, optional): Maximum iterations, for the YTM computation, Excel uses 100. Defaults to 100.

    Returns:
        _type_: _description_
    """    
    root = optimize.newton(f, x0, tol=tol, maxiter=max_iter)
    return root

