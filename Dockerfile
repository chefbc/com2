# Dockerfile used for local development of the site.
FROM python:latest

COPY *requirements.txt ./


RUN \
  pip install --no-cache-dir --upgrade pip \
&& \
  if [ -e requirements.txt ]; then \
    pip install -U -r requirements.txt; \
  fi 

WORKDIR /app
COPY *mkdocs.yml ./

EXPOSE 5000

