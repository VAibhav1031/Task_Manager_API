#!/bin/bash

# Check
# token_id=${1:?"Error: Please provide Token ID as argument 1"}
url=${1:?"Error: Please provide URL as argument 2"}
# -H "Authorization: Bearer $token_id" \
for i in {1..25}; do
    (
    curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"password" : "aryan_bond","email":"aryan40@gmail.com"}' \
    "$url" 
    ) &
done

wait

echo "DONE"
exit 0



