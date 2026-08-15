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
    customers = customers[customers['customer_mame'].str.len() >= 3]
    customers = customers.drop_duplicate(subset =['customer_id']) #hapus dupe

    #validasi kolom base_price 
    products = products[products['base_price'] > 0]
    products = products.drop_duplicate(subset = ['product_id']) 

    #validasi kolom status transaksi harus dalam kondisi "paid"
    orders = orders[orders['status'] == 'paid']
    #validasi kolom quantity dan price value tidak boleh < 0
    orders = orders[orders('quantity') > 0 and orders('price') > 0]
    orders = orders.drop_duplicate(subset = ['order_id'])

    return customers, products, orders

def load():
    pass

def main():
    customers, products, orders = extract()
    customers, products, orders = transform(customers, products, orders)
    load()

if __name__ == "__main__":
    main()





