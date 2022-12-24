FROM python:3

# ENV PYTHONDONTWRITEBYTECODE=1

# ENV PYTHONUNBUFFERED=1

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# ENV PATH=$PATH:/home/application/.local/bin

RUN useradd application

WORKDIR /home/application

RUN chown -R application:application /home/application

USER application

COPY --chown=application:application . .

RUN pip install -r requirements.txt  --user

# COPY . /code/