# Base Image
FROM python:3.8-slim-buster

# Working directory
WORKDIR /app

# Copy and install all required modules and libraries
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy all in working directory
COPY . .

# Execution command
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]