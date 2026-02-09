FROM python:3.11-slim

# Copy the requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

#OLD, remove:
# minimal deps
#RUN pip install --no-cache-dir flask requests python-dateutil

WORKDIR /app
COPY run.py /app/run.py

ENV FLASK_ENV=production
EXPOSE 80
CMD ["python", "run.py"]
