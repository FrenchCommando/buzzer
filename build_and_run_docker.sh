#!/bin/sh

docker build -t buzzerbuild .
docker run -d --rm -p 1337:1337 --cap-add=SYS_ADMIN --cap-add=NET_ADMIN --net=host -it buzzerbuild
