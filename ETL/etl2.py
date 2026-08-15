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

