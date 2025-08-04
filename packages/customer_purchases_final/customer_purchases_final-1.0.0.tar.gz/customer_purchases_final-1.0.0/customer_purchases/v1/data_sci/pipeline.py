import os
import numpy as np
import pandas as pd


class V1_sci:
    def _ingest(self, dataset_name, chunk_size):
        filtered_chunks = []

        df = pd.read_csv(dataset_name, chunksize=chunk_size)
        for chunk in df:
            chunk.dropna(how='all', inplace=True)
            chunk.drop_duplicates(inplace=True)

            required_columns = ['customer_id', 'product_category', 'purchase_amount',
                                'purchase_date', 'country_code', 'customer_age', 'payment_type']
            chunk.dropna(subset=required_columns, inplace=True)

            chunk['customer_id'] = pd.to_numeric(chunk['customer_id'], errors='coerce')
            chunk['purchase_amount'] = pd.to_numeric(chunk['purchase_amount'], errors='coerce')
            chunk['customer_age'] = pd.to_numeric(chunk['customer_age'], errors='coerce')
            chunk['purchase_date'] = pd.to_datetime(chunk['purchase_date'], errors='coerce')

            chunk.dropna(subset=['customer_id', 'purchase_amount', 'customer_age', 'purchase_date'], inplace=True)

            chunk = chunk[chunk['purchase_amount'] >= 0]
            chunk = chunk[chunk['customer_age'] >= 10]

            chunk.reset_index(drop=True, inplace=True)

            chunk['product_category'] = chunk['product_category'].astype('category')
            chunk['customer_id'] = pd.to_numeric(chunk['customer_id'], downcast='unsigned')
            chunk['customer_age'] = pd.to_numeric(chunk['customer_age'], downcast='float')
            chunk['country_code'] = chunk['country_code'].astype('category')
            chunk['payment_type'] = chunk['payment_type'].astype('category')
            chunk['purchase_amount'] = pd.to_numeric(chunk['purchase_amount'], downcast='float')

            filtered_chunks.append(chunk)

        return pd.concat(filtered_chunks)

    def _transform(self, dataset_name, chunk_size):
        data = self._ingest(dataset_name, chunk_size)

        # Feature engineering
        data['purchase_dayofweek'] = data['purchase_date'].dt.dayofweek
        data['purchase_month'] = data['purchase_date'].dt.month
        data.drop(columns=['purchase_date'], inplace=True)

        # Target
        y = data['product_category'].cat.codes

        # Features: encode categoricals
        X = data.drop(columns=['product_category'])
        X = pd.get_dummies(X, columns=['country_code', 'payment_type'])

        return X, y

    def load(self, dataset_name, chunk_size):
        X, y = self._transform(dataset_name, chunk_size)
        return X, y




















