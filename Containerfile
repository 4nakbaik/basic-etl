FROM python:3.13-slim

WORKDIR /ETL

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "etl1.py"]
