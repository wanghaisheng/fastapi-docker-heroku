FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

WORKDIR /app

COPY . /app

RUN ls -al 
RUN pip install -r requirements.txt

