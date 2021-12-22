FROM python:3.9.9
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "-u", "main.py", "--rub=100", "--eur=300", "--usd=200", "--period=600", "--debug=1"]