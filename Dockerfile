FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    default-libmysqlclient-dev \
    pkg-config \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files at build time
# Dummy values allow collectstatic to run without real secrets
RUN SECRET_KEY=build-placeholder \
    STRIPE_PUBLIC_KEY=pk_build_placeholder \
    STRIPE_SECRET_KEY=sk_build_placeholder \
    python manage.py collectstatic --noinput

EXPOSE ${PORT}

CMD exec gunicorn indoor_plant.wsgi:application --bind 0.0.0.0:${PORT} --workers 2 --threads 4 --timeout 120
