#!/bin/bash

source_folder="$1"
destination_folder="$2"

# Create the destination folder if it doesn't exist
mkdir -p "$destination_folder"

# Find JAR files recursively in the source folder and copy them to the destination folder
find "$source_folder" -type f -name "*.jar" -exec cp {} "$destination_folder" \;

echo "JAR files copied successfully from $source_folder to $destination_folder."