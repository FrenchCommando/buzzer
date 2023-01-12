#!/bin/sh

docker build -t buzzerbuild .
docker run -d -p 1337:1337 --cap-add=SYS_ADMIN --cap-add=NET_ADMIN --net=host --restart unless-stopped buzzerbuild
