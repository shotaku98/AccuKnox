# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /social_network

# Copy the current directory contents into the container at /app
COPY . /app

# Create and activate a virtual environment
RUN python -m venv venv
ENV PATH="/app/venv/bin:$PATH"

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt 
EXPOSE 8000

ENTRYPOINT ["python", "manage.py"]
CMD ["python", "manage.py", "makemigrations"]
CMD ["python", "manage.py", "migrate"]
CMD ["runserver", "0.0.0.0:8000"]
