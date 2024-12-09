FROM python:3.9-slim

WORKDIR /app

# Copy progect files
COPY requirements.txt ./
COPY app.py ./
COPY db.json ./
COPY test_script.py ./

# setup dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start app with gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]
