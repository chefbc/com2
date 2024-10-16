
```sh
docker-compose --project-name $(git rev-parse --abbrev-ref HEAD | tr '[:upper:]' '[:lower:]') run -it app bash
```



docker-compose --project-name $(git rev-parse --abbrev-ref HEAD | tr '[:upper:]' '[:lower:]') build app


