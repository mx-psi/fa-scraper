FROM python:3.7

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get -qq update && apt-get -qq install locales locales-all

# Copy project
COPY Pipfile /

# Install dependencies
RUN pip3 install pipenv && pipenv lock && pipenv install --system

COPY faScrap.py /