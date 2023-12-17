# Use the Python 3 base image
FROM python:3.8

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=true

RUN apt update && \
  apt install -y libpq-dev build-essential cron

# Set the working directory to /home/application
WORKDIR /home/application

# Switch to the application user

# Copy the application code and requirements.txt into the container
COPY  requirements.txt .


# Install Python packages from requirements.txt
RUN pip install -r requirements.txt

COPY  . .

# Make sure Django is installed
RUN python -m pip list 

# RUN python3 manage.py collectstatic --noinput

EXPOSE 8000

# Your CMD or ENTRYPOINT command here
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
