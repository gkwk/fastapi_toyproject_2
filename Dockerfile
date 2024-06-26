FROM python:3.11-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

RUN chmod +x /code/app/init.sh

WORKDIR /code/app

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
