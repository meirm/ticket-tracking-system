#!/bin/bash

for i in `cat .env`; do eval export $i;done
uvicorn main:main_app --port 8888 --reload