#!/bin/bash
docker login
docker tag py-tweets:latest wwonigkeit/py-tweets:latest
docker push wwonigkeit/py-tweets:latest