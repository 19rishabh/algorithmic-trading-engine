# Stage 1: Use an official Python runtime as a parent image
FROM python:3.10-slim

# Stage 2: Set the working directory inside the container
WORKDIR /app

# Stage 3: Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 4: Copy the rest of the application code into the container
COPY . .

# Stage 5: Expose the port the app will run on
EXPOSE 8000

# Stage 6: Define the command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]