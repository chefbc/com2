# Dockerfile used for local development of the site.
FROM python:3.11-alpine


COPY *requirements.txt ./

RUN \
  pip install --no-cache-dir --upgrade pip \
&& \
  if [ -e requirements.txt ]; then \
    pip install -U -r requirements.txt; \
  fi 

WORKDIR /docs

# Expose MkDocs development server port
#EXPOSE 8000
EXPOSE 8080

# Start development server by default
ENTRYPOINT ["mkdocs"]
# CMD ["serve", "--dev-addr=0.0.0.0:8000"]
