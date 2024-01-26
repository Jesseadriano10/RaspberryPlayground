#!/bin/bash

# Function to extract the seconds from a line
get_seconds() {
  line=$1
  seconds=$(echo "$line" | awk '{print $(NF-1)}')
  echo "$seconds"
}

# Read the file line by line and calculate the sum of seconds
sum=0
count=0
while IFS= read -r line; do
  seconds=$(get_seconds "$line")
  sum=$(echo "$sum + $seconds" | bc)
  count=$((count + 1))
done < "$1"

# Calculate the average seconds
average=$(echo "scale=4; $sum / $count" | bc)

echo "Average seconds: $average for file $1"