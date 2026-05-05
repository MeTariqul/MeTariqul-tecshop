#!/bin/bash
echo "BUILD START"
python3 -m pip install -r requirements.txt
cd techshop
python3 manage.py collectstatic --noinput --clear
cd ..
echo "BUILD END"
