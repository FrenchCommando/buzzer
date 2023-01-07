#!/bin/sh

docker build -t buzzerbuild .
docker run -d --rm -p 8890:8890 buzzerbuild
