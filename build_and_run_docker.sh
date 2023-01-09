#!/bin/sh

docker build -t buzzerbuild .
docker run --rm -p 1337:1337 buzzerbuild
