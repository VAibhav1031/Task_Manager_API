#!/bin/bash

# Check
token_id=${1:?"Error: Please provide Token ID as argument 1"}
url=${2:?"Error: Please provide URL as argument 2"}
# -H "Authorization: Bearer $token_id" \
for i in {1..150}; do
    (
    curl -s -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $token_id" \
    -d '{"title" : "test_bhai","description":"Please bear with me"}' \
    "$url" 
    ) &
done

wait

echo "DONE"
exit 0



