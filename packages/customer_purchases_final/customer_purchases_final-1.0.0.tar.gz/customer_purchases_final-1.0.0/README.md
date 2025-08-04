#

```python
# Basic chunked reading
import pandas as pd

chunksize = 100_000
reader = pd.read_csv('huge_orders.csv', chunksize=chunksize)
for chunk in reader:
    print(f"Chunk shape: {chunk.shape}")

# feltered_chunks = []
total_sales = 0
for chunk in pd.read_csv('huge_orders.csv', chunksize=100_000):
    chunk['total'] = chunk['quantity'] * chunk['price']
    total_sales += chunk['total'].sum()
print(total_sales)

# Filter and save to file
filtered_chunks = []
for chunk in pd.read_csv('huge_orders.csv', chunksize=100_000):
    filtered = chunk[chunk['country'] == 'USA']
    filtered_chunks.append(filtered)
## Combine and save
pd.concat(filtered_chunks)to_csv('usa_orders.csv', index=False)


# Unique value counting across chunks
uni_customers = set()
for chunk in pd.read_csv('huge_orders.csv', chunksize=100_000):
    unique_customers.update(chunk['customer_id'].unique())
print(len(unique_custormers))
```















