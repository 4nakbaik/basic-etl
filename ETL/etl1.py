# ETL(CSV to Posgresql) without Pandas
import csv
import re
import os
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Numeric
from sqlalchemy.orm import declarative_base, sessionmaker


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
base = declarative_base()

BASE_DIR = Path(__file__).resolve().parent
file_path = BASE_DIR.parent / 'Dataset' / 'transaksi1_raw.csv'

class Order(base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    order_date = Column(String(20))
    customer = Column(String(50))
    product = Column(String(50))
    price = Column(Numeric)
    quantity = Column(Integer)
    status = Column(String(20))
    total = Column(Numeric)
    category = Column(String(20))

Session = sessionmaker(engine)


def extract():
    with open(file_path, 'r', encoding = 'utf-8') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]

    return data

def transform(data):

    data_clean = []

    for row in data:
        try:
            quantity = int(row['quantity'])
            price = float(row['price'])
        except ValueError as e:
            print(f'Error Parse:{row} -> {e}')
            continue

        #Validasi
        if row['status'] != 'paid':
            continue

        if price <= 0 or quantity <= 0:
            continue

        #Standarisasi
        cleaned_name = re.sub(r'[^a-zA-Z\s]', '', row['customer']).strip().title()
        if not re.match(r'^[A-Za-z\s]{3,}$', cleaned_name):
            continue

        #Kolom baru
        total = price * quantity

        #Kategori
        if total > 5_000_000:
            category = 'Large'
        elif total > 1_000_000:
            category = 'Medium'
        else:
            category = 'Small'

        #Pair Data(karena date adlah tipe data psql)
        row['order_date'] = datetime.strptime(row.pop('date'), '%Y-%m-%d').date()

        data_clean.append({
            'id': int(row['id']),
            'order_date': row['order_date'],
            'customer':cleaned_name,
            'product': row['product'],
            'status': row['status'],
            'price': int(price),
            'quantity': quantity,
            'total': int(total),
            'category': category
        })

    return data_clean

def load(data):

    base.metadata.drop_all(engine) #Drop table jika ada
    base.metadata.create_all(engine) #Lalu buat table baru

    session = Session() 

    #Insert data
    try:

        for row in data:
            orders = Order(
                id = row['id'],
                order_date = row['order_date'],
                customer  = row['customer'],
                product = row['product'],
                status = row['status'],
                price = row['price'],
                quantity = row['quantity'],
                total = row['total'],
                category = row['category']
            )
            session.add(orders)

        session.commit()
        return True

    except Exception as e:
        session.rollback()
        print(f'Error: {e}')
        return False

    finally:
        session.close()
def main():
    
    print('Starting ETL....')

    data = extract()
    print(f'Extract: {len(data)} rows')

    data_clean = transform(data)
    print(f'Transform: {len(data_clean)} rows')

    success = load(data_clean)

    if success:
        print('Load success')
    else:
        print('Load error')


if __name__ == "__main__":
    main()