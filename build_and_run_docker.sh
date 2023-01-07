#!/bin/sh

docker build -t buzzerbuild .
docker run -d --rm -p 1339:1339 buzzerbuild
