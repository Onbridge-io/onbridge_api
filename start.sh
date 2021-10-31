#!/bin/bash

retry=10
echo -n "Trying migrations"
for i in $(seq $retry)
do
  echo -n .
  python manage.py migrate && break
  sleep 1
done

python3 createsuperuser.py
python3 manage.py collectstatic --noinput

echo "=Starting runserver="
gunicorn wsgi:application \
         --bind 0.0.0.0:80\
