from financebro.assets.fixed_income.bond import Bond


bond = Bond(cusip="123456789",
            isin="US123456789",
            price_percent=96.478,
            annual_coupon_rate_percent=3.950,
            coupon_period_days=180,
            next_coupon_date="04-23-2024",
            maturity_date="04-23-2027",
            settlement_date="04-03-2024",
            face_value=1000,
            ytm=5.211)

print(f"Return: {bond.total_return}")
print(f"APY: {bond.apy}")
print(f"Fidelity Yield to Maturity: {bond.ytm}")
print(f"Recomputed Yield to Maturity: {bond.compute_ytm(96.478)}")
print(f"Approximated Yield to Maturity: {bond.compute_approx_ytm(96.478)}")
print(f"Fidelity Price: {bond.price}")
print(f"Recomputed Price: {bond.compute_price(5.211)}")
print(f"Approximated Price: {bond.compute_approx_price(5.211)}")

