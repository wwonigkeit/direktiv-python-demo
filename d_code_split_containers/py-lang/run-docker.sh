#!/bin/bash
echo "Build the docker image"
docker build --tag py-lang .

echo "Check the docker images available"
docker images

echo "Running the docker image on port 8080"
docker run --publish 8080:8080 py-lang
