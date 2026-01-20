FROM python:3.11-slim

WORKDIR /app

COPY homebot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "homebot/main.py"]
