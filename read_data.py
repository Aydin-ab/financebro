#%%
import pandas as pd


df = pd.read_csv('data/fidelity_data.csv')
#%%
df.head()
# %%
df.columns
# %%
# Get 1 row as dict
example = df.iloc[0].to_dict()
print(example)
example['Cusip'] = example['Cusip'][2:-1]
print(example)

# %%
import financebro

bond = financebro.Bond(example['Cusip'],
                        example['Price Ask'],
                        example['Ask Yield to Maturity'],
                        example['Coupon'],
                        example['Maturity Date']
                        )

print(f"Return: {bond.total_return}")
print(f"APY: {bond.apy}")
print(f"Fidelity Price YTM 5%: {bond.compute_price(method='excel')}")
print(f"Fidelity Yield to Maturity 1000$: {bond.compute_ytm()}")
print(f"Number of coupons: {bond.num_coupons}, {bond.num_coupons_per_year}")
print(bond.coupon_dates)
print(f"Coupon period days: {bond.coupon_period_days}")
# %%
