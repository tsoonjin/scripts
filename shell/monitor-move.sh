#!/usr/bin/env bash

# Monitor directory for the event moved to and move it to target directory

inotifywait -m "$1" --format '%w%f' -e moved_to |
    while read file; do
        if [[ "$file" =~ .*mp4$ ]]; then
            echo $file
            mv "$file" "$2"
        fi
    done
