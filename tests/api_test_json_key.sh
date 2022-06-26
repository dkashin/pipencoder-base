#!/bin/bash

curl -d '{
  "api_key": "463ab59003404547a38763ec296e2173"
}' \
-H "Content-Type: application/json" -v http://localhost:8077/api/v1/logout
