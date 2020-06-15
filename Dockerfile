FROM python:3.7

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install package
RUN apt-get -qq update && apt-get -qq install locales locales-all
RUN pip3 install fa-scrapper
