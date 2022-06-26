#!/bin/bash

curl -d '{
  "username": "admin",
  "password": "admin"
}' \
-H "Content-Type: application/json" -v http://localhost:8077/api/v1/login
