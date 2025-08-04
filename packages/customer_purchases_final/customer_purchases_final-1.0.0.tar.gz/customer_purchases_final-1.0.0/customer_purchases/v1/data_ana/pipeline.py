import os
import numpy as np
import pandas as pd

class V1_ana:
    def _ingest(self, dataset_name, chunk_size):
        # Ingest analysis
        filtered_chunks = []

        df = pd.read_csv(dataset_name, chunksize=chunk_size)
        for chunk in df:
            # Drop empty rows
            chunk.dropna(how='all', inplace=True)

            # Drop duplicate rows
            chunk.drop_duplicates(inplace=True)

            # Remove rows with missing required fields
            required_columns = ['customer_id', 'purchase_id', 'product_category',
                                'purchase_amount', 'purchase_date',
                                'country_code', 'customer_age', 'payment_type']
            chunk.dropna(subset=required_columns, inplace=True)

            # Convert data types (where appropriate)
            chunk['customer_id'] = pd.to_numeric(chunk['customer_id'], errors='coerce')
            chunk['purchase_amount'] = pd.to_numeric(chunk['purchase_amount'], errors='coerce')
            chunk['customer_age'] = pd.to_numeric(chunk['customer_age'], errors='coerce')
            chunk['purchase_date'] = pd.to_datetime(chunk['purchase_date'], errors='coerce')

            # Drop rows where (conversions failed)
            chunk.dropna(subset=['customer_id', 'purchase_amount', 'customer_age', 'purchase_date'], inplace=True)

            # Remove implausible values
            chunk = chunk[chunk['purchase_amount'] >= 0]
            chunk = chunk[chunk['customer_age'] >= 10]

            # Optional: reset index
            chunk.reset_index(drop=True, inplace=True)

            # Optimize dtypes using downcasting strategies
            chunk['customer_id'] = pd.to_numeric(chunk['customer_id'], downcast='unsigned')
            chunk['purchase_id'] = chunk['purchase_id'].astype('category')
            chunk['product_category'] = chunk['product_category'].astype('category')
            chunk['purchase_amount'] = pd.to_numeric(chunk['purchase_amount'], downcast='float')
            chunk['purchase_date'] = chunk['purchase_date'].dt.date.astype('category')
            chunk['country_code'] = chunk['country_code'].astype('category')
            chunk['customer_age'] = pd.to_numeric(chunk['customer_age'], downcast='float')
            chunk['payment_type'] = chunk['payment_type'].astype('category')

            filtered_chunks.append(chunk)

        return pd.concat(filtered_chunks)

    def _transform(self, dataset_name, chunk_size):
        data = self._ingest(dataset_name, chunk_size)

        # Create age categories
        age_bins = [10, 18, 25, 35, 50, 65, 100]
        age_labels = ['10-17', '18-24', '25-34', '35-49', '50-64', '65+']
        data['age_category'] = pd.cut(data['customer_age'], bins=age_bins, labels=age_labels, right=False)

        # Extract season from purchase_date
        data['purchase_date'] = pd.to_datetime(data['purchase_date'])
        data['season'] = data['purchase_date'].dt.month % 12 // 3 + 1
        data['season'] = data['season'].map({1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Autumn'})

        # 1. Preferred product category by age category
        category_by_age = data.groupby('age_category', observed=False)['product_category'].agg(
            lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan
        )
        print("\nPreferred product category by age category:\n", category_by_age)

        # 2. Preferred product category by location (country)
        category_by_location = data.groupby('country_code', observed=False)['product_category'].agg(
            lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan
        )
        print("\nPreferred product category by location:\n", category_by_location)

        # 3. Number of sales by season
        sales_by_season = data['season'].value_counts().sort_index()
        print("\nSales count by season:\n", sales_by_season)

        # 4. Number of sales by season and age category
        sales_by_season_age = data.groupby(['season', 'age_category'], observed=False).size().unstack(fill_value=0)
        print("\nSales count by season and age category:\n", sales_by_season_age)

        # 5. Number of sales by season and location
        sales_by_season_location = data.groupby(['season', 'country_code'], observed=False).size().unstack(fill_value=0)
        print("\nSales count by season and location:\n", sales_by_season_location)

        return {
            'category_by_age': category_by_age,
            'category_by_location': category_by_location,
            'sales_by_season': sales_by_season,
            'sales_by_season_age': sales_by_season_age,
            'sales_by_season_location': sales_by_season_location,
        }

    def load(self, dataset_name, chunk_size):
        data = self._transform(dataset_name, chunk_size)
        return data













