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

  echo "checking model SYNC..."
  if ! psql -h dev-db --port=5432 -U ${DEV_DB_USER} -d ${DEV_DB_NAME} -tAc "SELECT 1 FROM information_schema.tables WHERE table_name='alembi_version'" | grep -q 1; then
    flask --app run.py db stamp head
  fi

  echo "Checking for model Changes"
  flask --app run.py db migrate -m "Auto migration" || echo "No model changes detected"
  flask --app run.py db upgrade
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
