#!/bin/bash

set -e

source ./.venv/bin/activate

until pg_isready --host=prod-db --port=5432 --dbname=${DB_NAME} --username=${DB_USER}; do
  echo "Waiting for the database to be ready.."
  sleep 2
done

echo "Database is ready!!"

export PGPASSWORD=${DB_PASSWORD}

echo "Setting up...."
if [ -d migrations/versions ] && [ "$(ls -A migrations/versions)" ]; then
  if ! psql -h prod-db --port=5432 -U ${DB_USER} -d ${DB_NAME} -tAc "SELECT 1 FROM information_schema.tables WHERE table_name='alembic_version';" | grep -q 1; then
    echo "No alembic_version table found, upgrading....."
    flask --app run.py db upgrade

  else

    if psql -h prod-db --port=5432 -U ${DB_USER} -d ${DB_NAME} -tAc "SELECT to_regclass('alembic_version');" | grep -q 'alembic_version'; then

      DB_VERSION=$(psql -h prod-db --port=5432 -U ${DB_USER} -d ${DB_NAME} -tAc "SELECT version_num FROM alembic_version LIMIT 1;")
    else
      DB_VERSION="none"
    fi

    HEAD_VERSION=$(flask --app run.py db heads | awk '{print $1}')

    echo "head_version : $HEAD_VERSION"

    if [ "$DB_VERSION" != "$HEAD_VERSION" ]; then
      echo "Migration version mismatch ($DB_VERSION -> $HEAD_VERSION), applying upgrade..."
      flask --app run.py db upgrade

    else
      echo "DB already up-to-date. Skipping upgrade."
    fi

  fi

else
  echo "No migration folder - intializing...."
  echo "This would never happen in the production"
fi

echo "Startting the flask application...."
exec uv run gunicorn --workers 8 -threads 4 -b 0.0.0.0:5555 run:app

