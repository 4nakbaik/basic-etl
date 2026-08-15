# ETL(CSV to Posgresql) with Pandas
import os
import re
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DB_URL = os.getenv('DATABASE_URL')
engine = create_engine(DB_URL)

BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR.parent / 'Dataset'

def extract():
    customers = pd.read_csv(DATASET_DIR / 'customers.csv')
    products = pd.read_csv(DATASET_DIR / 'products.csv')
    orders = pd.read_csv(DATASET_DIR / 'orders.csv')

    return customers, products, orders

def transform(customers, products, orders):
    #standarisasi
    customers['customer_name'] = customers['customer_name'].apply(
        lambda x: re.sub(r'[^a-zA-Z\s]', '', x).strip().title()
    )
    #validasi kolom customer_name min 3 char
    customers = customers[customers['customer_name'].str.len() >= 3]
    customers = customers.drop_duplicates(subset =['customer_id']) #hapus dupe

    #validasi kolom base_price 
    products = products[products['base_price'] > 0]
    products = products.drop_duplicates(subset = ['product_id']) 

    #filter kolom status transaksi harus dalam kondisi "paid"
    orders = orders[orders['status'] == 'paid']
    #filter kolom quantity dan total price value tidak boleh < 0
    orders = orders[(orders['quantity'] > 0) & (orders['total_price'] > 0)]
    orders = orders.drop_duplicates(subset = ['order_id'])

    return customers, products, orders

def load(customers, products, orders):
    
    customers.to_sql('dim_customers',engine, if_exists = 'replace', index = False)
    products.to_sql('dim_products',engine, if_exists = 'replace', index = False)
    orders.to_sql('fact_orders',engine, if_exists = 'replace', index = False)


def main():
    df_customers, df_products, df_orders = extract()
    cl_customers, cl_products, cl_orders = transform(df_customers, df_products, df_orders)
    success = load(cl_customers, cl_products, cl_orders)

    if success:
        print('Load success')
    else:
        print('Load error')     

if __name__ == "__main__":
    main()





