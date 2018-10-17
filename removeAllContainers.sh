#!/bin/bash

echo "REMOVING ALL CONTAINERS"
docker rm -f $(docker ps -a -q)

echo "BUILDING IMAGE"
docker build -t hw3 .

echo "RUNNING TEST SCRIPT"
python test_HW3.py

