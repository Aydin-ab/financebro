from financebro.assets.fixed_income.bond import Bond


print('\n')
print(f"DATE CONVENTION: us_nasd_30_360")
bond = Bond(cusip="123456789",
            price_percent=96.478,
            ytm_percent=5.211,
            annual_coupon_rate_percent=3.950,
            maturity_date="04-23-2027",
            settlement_date="04-03-2024",
            face_value=1000,
            date_convention="us_nasd_30_360")
print(f"Return: {bond.total_return}")
print(f"APY: {bond.apy}")
print(f"Fidelity Price YTM 5%: {bond.compute_price(method='excel')}")
print(f"Fidelity Yield to Maturity 1000$: {bond.compute_ytm()}")
print(f"Number of coupons: {bond.num_coupons}, {bond.num_coupons_per_year}")
print(bond.coupon_dates)
print(f"Coupon period days: {bond.coupon_period_days}")

