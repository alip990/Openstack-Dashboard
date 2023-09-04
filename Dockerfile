# Use the Python 3 base image
FROM python:3

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a user for running the application
RUN useradd application

# Set the working directory to /home/application
WORKDIR /home/application

# Change ownership of the /home/application directory to the application user
RUN chown -R application:application /home/application

# Switch to the application user
USER application

# Copy the application code and requirements.txt into the container
COPY --chown=application:application . .

# Install the Python packages listed in requirements.txt
RUN pip install -r requirements.txt

# Your CMD or ENTRYPOINT command here
