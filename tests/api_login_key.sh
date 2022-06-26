#!/bin/bash

curl -d '{
  "username": "admin",
  "password": "admin",
	"api_key_options":
	  {
	    "action": "create",
	    "key_ttl": 3600
	  }
}' \
-H "Content-Type: application/json" -v http://localhost:8077/api/v1/login
