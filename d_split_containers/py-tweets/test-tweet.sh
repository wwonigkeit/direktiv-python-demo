#!/bin/bash
curl -X POST -H "Direktiv-ActionID: Development" -d @input-tweet.json http://localhost:8080
