FROM python:3.13-alpine

# Set working directory ndani ya container
WORKDIR /app

# Weka mazingira salama ya Python (Zinazuia kutengeneza .pyc files na ku-buffer logs)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Weka mifumo ya Linux inayohitajika ku-compile maktaba kama psycopg2/asyncpg
RUN apk add --no-cache gcc musl-dev libffi-dev postgresql-dev

# Nakili requirements kwanza ili tufanye caching ya dependencies
COPY requirements.txt .

# Weka maktaba zote za Python zilizopo kwenye requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Nakili kodi yote ya backend iliyobaki kuingia ndani ya container
COPY . .

# Fungua port 8000 kwa ajili ya FastAPI API wetu
EXPOSE 8000

# Washa server ya Uvicorn kwa mfumo wa Live Reload wakati wa ujenzi
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
