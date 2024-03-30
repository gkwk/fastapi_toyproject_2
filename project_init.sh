#!/bin/bash

ENV_FILE=./app/.env

if [ -e $ENV_FILE ]; then
    sudo mkdir -p db models_store staticfile
    sudo docker-compose up --build
else
    echo "env file not found"
fi