#!/bin/bash

docker stop qabot || true
docker rm qabot || true
docker run -d --network=host -e TZ=Asia/Shanghai --name qabot --restart=always qabot
