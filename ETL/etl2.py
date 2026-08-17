# ETL(CSV to Posgresql) with Pandas
import os
import re
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.types import String, Integer, Float

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
    try:
        
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

    except Exception as e:
        print(f'Transform Error: {e}')
        return None

def load(customers, products, orders):
    try:
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS fact_orders CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS dim_products CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS dim_customers CASCADE;"))

            customers.to_sql('dim_customers',con=conn, if_exists = 'replace', index = False,
                dtype={
                    'product_id: Integer',
                    'product_name: String(150)',
            })
            products.to_sql('dim_products',con=conn, if_exists = 'replace', index = False,
                dtype={
                    'product_id: Integer',
                    'product_name: String(150)',
                    'base_price: Float'
                })
            orders.to_sql('fact_orders',con=conn, if_exists = 'replace', index = False)

        #Set primary key & foreign key
        with engine.begin() as conn:
            # pk
            conn.execute(text("ALTER TABLE dim_customers ADD PRIMARY KEY (customer_id);"))
            conn.execute(text("ALTER TABLE dim_products ADD PRIMARY KEY (product_id);"))
            conn.execute(text("ALTER TABLE fact_orders ADD PRIMARY KEY (order_id);"))

            # fk
            conn.execute(text("""
                ALTER TABLE fact_orders 
                ADD CONSTRAINT fk_order_customer 
                FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id)
                ON DELETE CASCADE;
            """))

            conn.execute(text("""
                ALTER TABLE fact_orders 
                ADD CONSTRAINT fk_order_product 
                FOREIGN KEY (product_id) REFERENCES dim_products(product_id)
                ON DELETE CASCADE;
            """))
        return True

    except Exception as e:
        print(f'Load Error:{e}')
        return False
    

def main():

    print('Starting ETL....')

    df_customers, df_products, df_orders = extract()
    print(f'Extract length: {len(df_customers)} rows, {len(df_products)} rows, {len(df_orders)} rows')

    cl_customers, cl_products, cl_orders = transform(df_customers, df_products, df_orders)
    print(f'Transform length: {len(cl_customers)} rows, {len(cl_products)} rows, {len(cl_orders)} rows')

    success = load(cl_customers, cl_products, cl_orders)

    if success:
        print('Load success')
    else:
        print('Load failed')   

if __name__ == "__main__":
    main()





