#!/bin/bash

# Output file
output="combined_output.txt"
> "$output"  # Empty the file if it already exists

# Loop over files (not directories)
for file in *; do
  if [ -f "$file" ]; then
    echo "=== $file ===" >> "$output"
    cat "$file" >> "$output"
    echo -e "\n" >> "$output"
  fi
done

