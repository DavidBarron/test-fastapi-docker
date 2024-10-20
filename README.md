# test-fastapi-docker
Simple Fast API application that demonstrates using Mongo and Redis (Memorystore for Redis) for distributed actions.

## Local Setup
Make sure we have [Docker](https://docs.docker.com/desktop/install/mac-install/) installed.
### Setup Mongo and Redis
Pull the latest images of Mongo and Redis from DockerHub and run as containers.
```shell
docker pull redis
docker pull mongodb/mongodb-community-server:latest

docker run --name redis -p 6379:6379 -d redis
docker run --name mongodb -p 27017:27017 -d mongodb/mongodb-community-server:latest
```
Set up a virtualenv and run application.
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

uvicorn src.main:create_application --host 0.0.0.0 --port 8080 --factory
```


### Stress test
Simulate high traffic using [ApacheBench](https://httpd.apache.org/docs/2.4/programs/ab.html) by sending 100 GET requests across 10 processes.
```shell
ab -n 100 -c 10 http://127.0.0.1:8080/bump
ab -n 100 -c 10 http://127.0.0.1:8080/bump-lock
```
