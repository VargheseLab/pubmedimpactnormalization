FROM python:3.11-slim

# Export with settings configuration
ARG SKIP_CURRENT_YEAR
ENV SKIP_CURRENT_YEAR=true

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
COPY utils/ utils/
COPY static/ static/
COPY templates/ templates/
COPY app.py app.py

EXPOSE 8080
CMD [ "gunicorn", "-w 4", "-b :8080", "--preload", "app:app" ]
