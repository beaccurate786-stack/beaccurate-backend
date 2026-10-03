#!/bin/sh
set -eu

python - <<'PY'
import os
import time

import MySQLdb

connection_settings = {
    'host': os.environ.get('MYSQL_HOST', 'db'),
    'port': int(os.environ.get('MYSQL_PORT', '3306')),
    'user': os.environ['MYSQL_USER'],
    'passwd': os.environ['MYSQL_PASSWORD'],
    'db': os.environ['MYSQL_DATABASE'],
}

for attempt in range(30):
    try:
        connection = MySQLdb.connect(connect_timeout=3, **connection_settings)
        connection.close()
        break
    except MySQLdb.OperationalError:
        if attempt == 29:
            raise
        time.sleep(1)
PY

python manage.py runserver 0.0.0.0:8000
