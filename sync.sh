#!/bin/bash
rsync -av --dry-run --size-only  --include  pages/migrations/__init__.py  --exclude postges_data --exclude .git --exclude __pycache__/ --exclude 'migrations/*_*.*' . meirm@tts:/opt/django_project/.

echo "Do you want to sync the files? (y/N)"
read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
    rsync -av --size-only  --include  pages/migrations/__init__.py  --exclude postges_data --exclude .git --exclude __pycache__/ --exclude 'migrations/*_*.*' . meirm@tts:/opt/django_project/.
fi