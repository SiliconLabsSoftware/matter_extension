#!/bin/bash

# Get directory from argument or use current directory as default
SEARCH_DIR="${1:-.}"

# Get output file name from argument or use default
OUTPUT_FILE="${2:-code_size_results.csv}"

# Write CSV header
echo "file_path,text_size,bss_data_size" > "$OUTPUT_FILE"

# Find all .out files in the specified directory and subdirectories
find "$SEARCH_DIR" -name "*.out" -type f | while read -r file; do
    # Run arm-none-eabi-size and capture output
    size_output=$(arm-none-eabi-size "$file" 2>/dev/null)
    
    # Check if the command succeeded
    if [ $? -eq 0 ]; then
        # Extract text, data, and bss values (skip header line, get second line)
        values=$(echo "$size_output" | tail -n 1)
        
        # Parse the values (typical format: text data bss dec hex filename)
        text=$(echo "$values" | awk '{print $1}')
        data=$(echo "$values" | awk '{print $2}')
        bss=$(echo "$values" | awk '{print $3}')
        
        # Calculate bss + data
        bss_data_total=$((bss + data))
        
        # Replace commas in file path with underscores for CSV compatibility
        file_sanitized="${file//,/_}"
        
        # Write to CSV
        echo "$file_sanitized,$text,$bss_data_total" >> "$OUTPUT_FILE"
    else
        echo "Warning: Failed to process $file" >&2
    fi
done

echo "Results saved to $OUTPUT_FILE"
