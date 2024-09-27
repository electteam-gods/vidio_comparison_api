FROM python:3.12.2

RUN apt-get update && apt-get install -y \
    curl \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --upgrade -r /code/requirements.txt

RUN pip install uvicorn

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]