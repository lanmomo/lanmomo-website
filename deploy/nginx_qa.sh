#!/bin/bash
nginx_file=$(ls -1 /etc/nginx/sites-enabled/*lanmomo.org)
nginx_file_count=$(echo "$nginx_file" | wc -l)

if [[ ! $(echo "$nginx_file" | wc -l) -eq 1 ]]; then
    echo "Found ${nginx_file_count} nginx configs matching lanmomo... Expected 1.";
    exit 1
fi

current=$(ls ../public/partials/ | cut -d '.' -f 1 | sort | paste -sd "|" -)
nginx=$(grep rewrite "$nginx_file" | cut -f 2 -d "(" | cut -f 1 -d ")")

if [ "$current" != "$nginx" ]; then
    tmp_file=$(mktemp /tmp/XXXXXXXX)
    cp "$nginx_file" "$tmp_file"
    sed -i "s/$nginx/$current/" "$tmp_file"
    echo "HOLD ON M8y, this config looks BORKED! Here's what you should do:"
    diff "$nginx_file" "$tmp_file"
    rm "$tmp_file"
else
    echo "Nginx rewrites look consistant with current partials."
fi
