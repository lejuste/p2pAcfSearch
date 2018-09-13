#!/bin/bash

echo "REMOVING ALL IMAGES"

docker rmi $(docker images -a -q)
