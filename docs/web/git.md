
```sh
git checkout origin/main docker-compose.yml
```



```sh
git push origin $(git rev-parse --abbrev-ref HEAD) -o ci.skip
```


[terminus](https://www.warp.dev/terminus/undo-a-git-push)