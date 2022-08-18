#!/bin/bash
docker login
docker tag py-lang:latest wwonigkeit/py-lang:latest
docker push wwonigkeit/py-lang:latest