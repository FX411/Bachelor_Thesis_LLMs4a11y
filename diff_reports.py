#!/bin/usr/env python

import json
import sys

def load_json(file_path):
    """Load JSON data from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error loading JSON file {file_path}: {e}")
        sys.exit(1)

def compare_json(file1, file2, output_file):
    """Compare total, passes, and errors from two JSON files and save the differences."""
    data1 = load_json(file1)
    data2 = load_json(file2)

    diff = {}

    keys_to_compare = ["total", "passes", "errors"]

    for key in keys_to_compare:
        if key in data1 and key in data2:
            if data1[key] != data2[key]:
                diff[key] = {
                    "file1": data1[key],
                    "file2": data2[key],
                    "difference": data2[key] - data1[key]
                }
        else:
            print(f"⚠ Key '{key}' not found in one of the files.")

    if diff:
        with open(output_file, "w", encoding="utf-8") as diff_file:
            json.dump(diff, diff_file, indent=2)

        print(f"✅ Differences saved to {output_file}")
        print(json.dumps(diff, indent=2))  # Print diff in the terminal
    else:
        print("✅ No differences found.")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python compare_json.py <file1.json> <file2.json> <output_file.json")
        sys.exit(1)

    compare_json(sys.argv[1], sys.argv[2], sys.argv[3])
