# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
COPY . .

# Defines the command to run when the container starts.
# This can be overridden in docker-compose.yml or with `docker run`.
# For example, to run the inference service, you would use:
# CMD ["python", "inference_service/app.py"]
CMD ["bash"]
