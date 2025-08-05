# Stage 1: Use an official Python runtime as a parent image
FROM python:3.11-slim

# Stage 2: Install system-level dependencies required by LightGBM
RUN apt-get update && apt-get install -y libgomp1

# Stage 3: Set the working directory inside the container
WORKDIR /app

# Stage 4: Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 5: Copy the rest of the application code into the container
COPY . .

# Stage 6: Run the data pipeline to generate the results files
RUN python main.py

# Stage 7: Expose the port the app will run on
EXPOSE 8000

# Stage 8: Define the command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]