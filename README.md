# test-fastapi-docker

### Setup Redis
```shell
docker pull redis
```

### Stress test
```shell
ab -n 100 -c 10 http://127.0.0.1:8080/bump
```
