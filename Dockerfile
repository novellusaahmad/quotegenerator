# Novellus Loan Management System - Azure Container Apps Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=main.py
ENV FLASK_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies required for WeasyPrint and other packages
RUN set -eux; \
    apt-get update; \
    # Determine correct gdk-pixbuf package name for the base distro
    if apt-cache show libgdk-pixbuf-xlib-2.0-0 >/dev/null 2>&1; then \
        PIXBUF_PKG=libgdk-pixbuf-xlib-2.0-0; \
    else \
        PIXBUF_PKG=libgdk-pixbuf-2.0-0; \
    fi; \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      gcc \
      g++ \
      libpango-1.0-0 \
      libpangoft2-1.0-0 \
      libffi-dev \
      "$PIXBUF_PKG" \
      libgtk-3-0 \
      libcairo-gobject2 \
      libcairo2 \
      shared-mime-info; \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY Requirements.txt .
RUN pip install --no-cache-dir -r Requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads reports_output static/css static/js templates

# Set permissions
RUN chmod +x start.sh 2>/dev/null || true

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "main:app"]
