#!/bin/bash

curl -X POST \
-H "X-API-KEY: 67860ba5cae347e983b1481fc6aaa272" \
-H "Content-Type: application/json" \
-v http://localhost:8077/api/v1/user/list
