# define an alias for the specfic python version used in this file.
FROM python:3.10-slim-bullseye as python

# Set the working directory in the container
WORKDIR /code

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y 

# Copy the dependencies file to the working directory
COPY requirements.txt /code/

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . /code/