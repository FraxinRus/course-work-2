FROM python:3.8

WORKDIR /app

ENV PYTHONPATH /app

COPY requirements.txt requirements.txt

COPY ./model /app/model

COPY ./view/templates /app/templates

RUN pip install -r requirements.txt

RUN pip install mysql-connector-python==8.0.26

COPY . .

CMD ["python", "controller/game_controller.py"]