FROM python:3.11-slim

# minimal deps
RUN pip install --no-cache-dir flask requests python-dateutil

WORKDIR /app
COPY run.py /app/run.py

ENV FLASK_ENV=production
EXPOSE 80
CMD ["python", "run.py"]
