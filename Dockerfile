FROM python:3.11-slim

# System dependencies for Playwright (Chromium) and WeasyPrint on Debian Trixie
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Chromium / Playwright
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2t64 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxext6 \
    libxi6 \
    libxtst6 \
    fonts-liberation \
    # WeasyPrint / Cairo
    libcairo2 \
    libgdk-pixbuf-xlib-2.0-0 \
    libffi-dev \
    shared-mime-info \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install chromium

COPY . .

RUN chmod +x entrypoint.sh

RUN mkdir -p staticfiles media data

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
