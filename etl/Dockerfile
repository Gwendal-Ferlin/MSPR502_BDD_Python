FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY extract.py load.py main.py transform.py ./
COPY data/ ./data/

CMD ["python", "main.py"]
