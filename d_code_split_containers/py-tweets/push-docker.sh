#!/bin/bash
docker login
docker tag py-tweets-lang:latest wwonigkeit/py-tweets:latest
docker push wwonigkeit/py-tweets:latest