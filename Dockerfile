# Use the Python 3 base image
FROM python:3

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=true

RUN apt update && \
  apt install -y libpq-dev build-essential netcat cron

# Create a user for running the application
RUN useradd application

# Set the working directory to /home/application
WORKDIR /home/application

# Change ownership of the /home/application directory to the application user
RUN chown -R application:application /home/application

# Switch to the application user
USER application

# Copy the application code and requirements.txt into the container
COPY --chown=application:application requirements.txt .


# Install Python packages from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=application:application . .

# Make sure Django is installed
RUN python -m pip list 

RUN python3.8 manage.py collectstatic --noinput

EXPOSE 8000

# Your CMD or ENTRYPOINT command here
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
