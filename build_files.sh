#!/bin/bash
echo "BUILD START"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd techshop
python manage.py collectstatic --noinput --clear
cd ..
echo "BUILD END"
