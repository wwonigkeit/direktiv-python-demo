#!/bin/bash
curl -X POST -H "Direktiv-ActionID: Development" -d @/tmp/output.json http://localhost:8080
