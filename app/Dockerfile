# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip3 install -r requirements.txt

# Copy the rest of the application code into the container
COPY . .


# Set environment variables for the database connection
ENV DB_HOST=db
ENV DB_PORT=5432
ENV DB_NAME=hair_booking_dev
ENV DB_USER=hair_booking
ENV DB_PASSWORD=password

#Start the Flask app
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]


