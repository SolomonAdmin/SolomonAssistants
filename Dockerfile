# Use an official Python 3.9 base image (amd64 architecture for compatibility)
FROM --platform=linux/amd64 python:3.9-slim-bullseye

WORKDIR /app

# Install system dependencies including ODBC libraries and build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    unixodbc unixodbc-dev \ 
    gnupg curl build-essential && \ 
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Add Microsoft SQL Server ODBC driver repository and install the ODBC Driver 17
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install any additional libraries needed by the ODBC driver (e.g., Kerberos support)
RUN apt-get update && apt-get install -y libgssapi-krb5-2 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy dependency definitions
COPY requirements-minimal.txt /app/
COPY constraints.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-minimal.txt

# Copy the application code into the image
COPY ./app /app/app
COPY ./helpers /app/helpers
COPY ./config.py /app/

# Set PYTHONPATH so the app package is recognized
ENV PYTHONPATH="/app:/app/app"

# Expose the application port (Render will port-map this if needed)
EXPOSE 80

# Start the FastAPI application with Uvicorn, using Render's PORT if available
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-80}"]
