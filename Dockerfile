# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./app /app/app
COPY ./tools /app/tools
COPY tools_config.py requirements.txt /app/
COPY .env /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV MODULE_NAME="app.main"
ENV VARIABLE_NAME="app"
ENV PORT=80

# Run the application
CMD uvicorn $MODULE_NAME:$VARIABLE_NAME --host 0.0.0.0 --port $PORT