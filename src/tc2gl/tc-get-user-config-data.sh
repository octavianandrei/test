#!/bin/bash

# Define source and destination file paths
SOURCE_FILE="/opt/buildagent/temp/buildTmp/teamcity.config.parameters"
DESTINATION_FILE="/opt/buildagent/temp/buildTmp/teamcity.subset.config.parameters"

# Create or clear the destination file
> "$DESTINATION_FILE"

# Read the source file line by line
while read -r line; do
    # Check if the line does not start with the specified words or #
    if [[ ! $line =~ ^(teamcity|DotNet|podman|python|build|#) ]]; then
        # Write the line to the destination file
        echo "$line" >> "$DESTINATION_FILE"
    fi
done < "$SOURCE_FILE"

echo "Lines starting with teamcity, DotNet, podman, python, build, or # have been stripped from $SOURCE_FILE and written to $DESTINATION_FILE"
