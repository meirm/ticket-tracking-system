#1/bin/bash

# This script is used to push the code to the production server
# The code is pushed to the production server using rsync

#first ask the production server to backup the db.sqlite3 file
ssh pi@192.168.0.21 "cd tts; cp db.sqlite3 db.sqlite3.bak-$(date +%Y-%m-%d-%H-%M-%S)"

# Second push the code to the production server
rsync -av . --exclude settings.py --exclude */migrations/* --exclude db.sqlite3 pi@192.168.0.21:tts/.
