FROM fsfe/pipenv:python-3.8
RUN apt-get update && \
    apt-get install -y --no-install-recommends git build-essential
WORKDIR /app
COPY . .
RUN pipenv install
CMD ["/app/run-docker.sh"]
