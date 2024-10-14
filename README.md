# test-fastapi-docker

### Setup Redis
Pull the latest image of the Redis container from DockerHub
```shell
docker pull redis
```

### Stress test
Simulate high traffic by sending 100 GET requests across 10 processes.
```shell
ab -n 100 -c 10 http://127.0.0.1:8080/bump
```
