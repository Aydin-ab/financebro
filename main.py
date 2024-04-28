import financebro

SETTLEMENT_DATE = '04/27/2024'

print(f"\n\n BOND WITH NO COUPON PERIOD BEFORE MATURITY BUT QTY > 1\n\n")
bond = financebro.Bond('025816CV9', 
                       99.953, 
                       8.872, 
                       3.375, 
                       '05/03/2024',
                       coupon_period_days=180,
                       settlement_date=SETTLEMENT_DATE)

#bonds, callable_bonds = financebro.preprocess_fidelity_data('fidelity_data.csv')

print(f"Return: {bond.total_return}")
print(f"APY: {bond.apy}")
print(f"Fidelity Price: {bond.compute_price(method='excel')}")
print(f"Fidelity Yield to Maturity: {bond.compute_ytm_percent()}")
print(f"Number of coupons: {bond.num_coupons}, {bond.num_coupons_per_year}")
print(f"Is correct ? {round(bond.compute_ytm_percent(), 3) == 8.872 and round(bond.compute_price(method='excel'), 3) == 99.953}")



print(f"\n\n BOND WITH NO COUPON PERIOD BEFORE MATURITY BUT QTY 1\n\n")
bond = financebro.Bond('25152RXA6', 
                       100.084, 
                       2.649, 
                       3.700, 
                       '05/30/2024',
                       coupon_period_days=180,
                       settlement_date=SETTLEMENT_DATE)

print(f"Return: {bond.total_return}")
print(f"APY: {bond.apy}")
print(f"Fidelity Price: {bond.compute_price(method='excel')}")
print(f"Fidelity Yield to Maturity: {bond.compute_ytm_percent()}")
print(f"Number of coupons: {bond.num_coupons}, {bond.num_coupons_per_year}")
print(f"Is correct ? {round(bond.compute_ytm_percent(), 3) == 2.649 and round(bond.compute_price(method='excel'), 3) == 100.084}")




print(f"\n\n BOND WITH > 1 COUPON PERIOD BEFORE MATURITY BUT QTY > 1\n\n")
bond = financebro.Bond('24422EXD6', 
                       100.024, 
                       5.136, 
                       5.150, 
                       '09/08/2026',
                       coupon_period_days=180,
                       settlement_date=SETTLEMENT_DATE)

#bonds, callable_bonds = financebro.preprocess_fidelity_data('fidelity_data.csv')

print(f"Return: {bond.total_return}")
print(f"APY: {bond.apy}")
print(f"Fidelity Price: {bond.compute_price(method='excel')}")
print(f"Fidelity Yield to Maturity: {bond.compute_ytm_percent()}")
print(f"Number of coupons: {bond.num_coupons}, {bond.num_coupons_per_year}")
print(f"Is correct ? {round(bond.compute_ytm_percent(), 3) == 5.136 and round(bond.compute_price(method='excel'), 3) == 100.024}")



print(f"\n\n BOND WITH > 1 COUPON PERIOD BEFORE MATURITY BUT QTY 1\n\n")
bond = financebro.Bond('6174467Y9', 
                       97.339, 
                       5.568, 
                       4.350, 
                       '09/08/2026',
                       coupon_period_days=180,
                       settlement_date=SETTLEMENT_DATE)

#bonds, callable_bonds = financebro.preprocess_fidelity_data('fidelity_data.csv')

print(f"Return: {bond.total_return}")
print(f"APY: {bond.apy}")
print(f"Fidelity Price: {bond.compute_price(method='excel')}")
print(f"Fidelity Yield to Maturity: {bond.compute_ytm_percent()}")
print(f"Number of coupons: {bond.num_coupons}, {bond.num_coupons_per_year}")
print(f"Is correct ? {round(bond.compute_ytm_percent(), 3) == 5.568 and round(bond.compute_price(method='excel'), 3) == 97.339}")



print(f"\n\n BOND WITH 1 COUPON PERIOD BEFORE MATURITY\n\n")
bond = financebro.Bond('78015K7C2', 
                       98.416, 
                       5.487, 
                       2.250, 
                       '11/01/2024',
                       coupon_period_days=180,
                       settlement_date=SETTLEMENT_DATE)

#bonds, callable_bonds = financebro.preprocess_fidelity_data('fidelity_data.csv')

print(f"Return: {bond.total_return}")
print(f"APY: {bond.apy}")
print(f"Fidelity Price: {bond.compute_price(method='excel')}")
print(f"Fidelity Yield to Maturity: {bond.compute_ytm_percent()}")
print(f"Number of coupons: {bond.num_coupons}, {bond.num_coupons_per_year}")
print(f"Is correct ? {round(bond.compute_ytm_percent(), 3) == 5.487 and round(bond.compute_price(method='excel'), 3) == 98.416}")



hey = 0
