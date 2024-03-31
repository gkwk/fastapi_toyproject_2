#!/bin/bash

DB_FILE=./db/test.sqlite
ALEMBIC_TEMPLATE_FOLDER=./alembic_template_sqlite
ALEMBIC_TEMPLATE_FOLDER_ABSOLUTE_PATH=$(realpath "$ALEMBIC_TEMPLATE_FOLDER")

if [ -e $DB_FILE ]; then
	uvicorn main:app --host 0.0.0.0 --port 8000 --proxy-headers
else
    alembic init -t "$ALEMBIC_TEMPLATE_FOLDER_ABSOLUTE_PATH" migrations
    alembic revision --autogenerate
    alembic upgrade head
    uvicorn main:app --host 0.0.0.0 --port 8000 --proxy-headers
fi