#!/usr/bin/env bash

KEEP=10

echo "=-> Deleting web-stream tags..."
oc describe is/web-stream | \
    grep ^latest-[1-9] | \
    cut -d- -f2 | sort -nr | \
    awk -v s=$KEEP 'NR>s' | \
    awk '{system("oc delete istag/web-stream:latest-"$1)}'

echo "=-> Deleting loader-stream tags..."
oc describe is/loader-stream | \
    grep ^latest-[1-9] | \
    cut -d- -f2 | \
    sort -nr | \
    awk -v s=$KEEP 'NR>s' | \
    awk '{system("oc delete istag/loader-stream:latest-"$1)}'

echo "=-> Pruning images..."
oc adm prune images --force-insecure --confirm
