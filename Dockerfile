# Use the Python 3 base image
FROM python:3

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=true


# Create a user for running the application
RUN useradd application

# Set the working directory to /home/application
WORKDIR /home/application

RUN mkdir -p /home/application/.cache/pip
RUN chown -R application:application /home/application/.cache/pip

# Change ownership of the /home/application directory to the application user
RUN chown -R application:application /home/application

# Switch to the application user
USER application

# Copy the application code and requirements.txt into the container
COPY --chown=application:application . .

# Install Python packages from requirements.txt
RUN pip install --no-warn-script-location -r requirements.txt

# Make sure Django is installed
RUN python -m pip list 

# Your CMD or ENTRYPOINT command here
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
