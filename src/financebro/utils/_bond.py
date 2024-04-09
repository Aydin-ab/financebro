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