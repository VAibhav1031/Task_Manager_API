#!/bin/bash

set -e

source ./.venv/bin/activate

until pg_isready --host=dev-db --port=5432 --dbname=${DEV_DB_NAME} --username=${DEV_DB_USER}; do
  echo "Waiting for the database to be ready.."
  sleep 2
done

echo "Database is ready!!"

export PGPASSWORD=${DEV_DB_PASSWORD}
# # cause flask  app container is different then the dev-db , so for the psql command in postgres  connection to local peer is Trust no password
# # but since flask app contaiener run on different ip (network) so it need the TCP for connection for that defualt is md5 which is password requirement

echo "Setting up...."
if [ -d migrations/versions ] && [ "$(ls -A migrations/versions)" ]; then

  if ! psql -h prod-db --port=5432 -U ${DB_USER} -d ${DB_NAME} -tAc "SELECT 1 FROM information_schema.tables WHERE table_name='alembic_version'" | grep -q 1; then
    echo "checking model SYNC..."
    flask --app run.py db stamp head
  fi

  if ! flask db heads | grep -q $(psql -h prod-db ... -c "SELECT version_num FROM alembic_version" -tA); then
    echo "Migration version mismatch, applying upgrade..."
    flask db upgrade
  else
    echo "DB already up-to-date. Skipping upgrade."
  fi

else
  echo "No migration folder - intializing...."
  echo "Creating...."

  flask --app run.py db init
  flask --app run.py db migrate -m "initial migration"
  flask --app run.py db upgrade
fi

echo "Startting the flask application...."
exec uv run python run.py

# flow is  like this   check_if_db_is_ready -> check_migration_folder -> if the migrations script not there -> create_initials & migrate -> db upgrade --> run application

# few point if  i make changes in the migration folder in the host and  run the application again and all
# when it is running and when not
