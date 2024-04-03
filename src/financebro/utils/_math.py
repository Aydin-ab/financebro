import datetime
import calendar
import scipy.optimize as optimize



def day_diff(start_time: str, end_time: str, date_convention= 'us_nasd_30_360') -> datetime.timedelta:
    if date_convention == 'normal':
        return day_diff_normal(start_time, end_time)
    elif date_convention == 'us_nasd_30_360':
        return day_diff_us_nasd_30_360(start_time, end_time, excel= True)
    else:
        raise ValueError(f"Invalid mode: {date_convention}")

def day_diff_normal(start_time: str, end_time: str) -> int:
    # Convert string of format MM-DD-YYYY to datetime object
    start_time = datetime.datetime.strptime(start_time, "%m-%d-%Y")
    end_time = datetime.datetime.strptime(end_time, "%m-%d-%Y")
    diff = end_time - start_time
    days = diff.days
    return days

def day_diff_us_nasd_30_360(start_time: str, end_time: str, excel= True) -> int:
    # https://sqlsunday.com/2014/08/17/30-360-day-count-convention/ 
    # Convert string of format MM-DD-YYYY to datetime object
    start_time = datetime.datetime.strptime(start_time, "%m-%d-%Y")
    end_time = datetime.datetime.strptime(end_time, "%m-%d-%Y")
    start_day = start_time.day
    start_month = start_time.month
    end_day = end_time.day
    end_month = end_time.month
    if start_month == 2 and start_day == calendar.monthrange(start_time.year, start_month)[1]:
        start_day = 30
        if not excel and end_day == calendar.monthrange(end_time.year, end_month)[1]:
        # Excel seems to forget that rule...
        # Try ('02-29-2024', '02-29-2024') or ('02-29-2024', '02-28-2025') they should return 0 and 360 respectively but here it doesn't..
        # That condition here fixes it
            end_day = 30
    if start_day == 31:
        start_day = 30
    if end_day == 31 and start_day == 30:
        end_day = 30
    days = 360 * (end_time.year - start_time.year) + 30 * (end_month - start_month) + (end_day - start_day)
    return days
     

def solve_newton(f, x0, tol=1e-10, max_iter=100):
    root = optimize.newton(f, x0, tol=tol, maxiter=max_iter)
    return root

