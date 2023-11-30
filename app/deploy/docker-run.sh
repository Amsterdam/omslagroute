#!/usr/bin/env bash
# set -u   # crash on missing env variables
set -e   # stop on any error
set -x

python manage.py collectstatic --settings settings.settings --no-input
python manage.py migrate --settings settings.settings --no-input

if [ -n "${ADMIN_USERNAME}" ] && [ -n "${ADMIN_PASSWORD}" ]; then
  python manage.py initadmin --settings settings.settings --username $ADMIN_USERNAME --password $ADMIN_PASSWORD
fi


exec uwsgi uwsgi.ini
