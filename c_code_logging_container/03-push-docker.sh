#!/bin/bash
docker login
docker tag py-tweets-lang:latest wwonigkeit/py-tweets-lang:latest
docker push wwonigkeit/py-tweets-lang:latest