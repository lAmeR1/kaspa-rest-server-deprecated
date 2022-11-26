#!/bin/sh
docker run --rm -it -p 8000:8000 -e KASPAD_HOST_1=192.168.168.3:16110 supertypo/kaspa-rest-server:latest

