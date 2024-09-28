FROM nvidia/cuda:12.4.0

# Установка необходимых зависимостей
RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Добавление PPA для Python 3.12
RUN add-apt-repository ppa:deadsnakes/ppa

# Обновление списка пакетов и установка Python 3.12
RUN apt-get update && apt-get install -y python3.12 python3.12-venv python3.12-dev

# Установка pip для Python 3.12
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.12 get-pip.py && rm get-pip.py

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --upgrade -r /code/requirements.txt

RUN pip install uvicorn

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]