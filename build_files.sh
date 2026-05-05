#!/bin/bash
echo "BUILD START"
python3.9 -m pip install -r requirements.txt
cd techshop
python3.9 manage.py collectstatic --noinput --clear
cd ..
echo "BUILD END"
