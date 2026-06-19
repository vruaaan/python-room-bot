FROM python:3.12-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# firebaseaccount.json and venues.json must be present in this folder before building

CMD ["python", "main.py"]
