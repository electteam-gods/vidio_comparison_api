FROM nvidia/cuda:12.4.0-devel-ubuntu22.04
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Установка необходимых зависимостей
RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Добавление PPA для Python 3.11
RUN add-apt-repository ppa:deadsnakes/ppa

# Обновление списка пакетов и установка Python 3.11
RUN apt-get update && apt-get install -y python3.11 python3.11-venv python3.11-dev

# Установка pip для Python 3.11
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.11 get-pip.py && rm get-pip.py

# Устанавливаем PyTorch с поддержкой CUDA
RUN pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu124

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --upgrade -r /code/requirements.txt

RUN pip install uvicorn

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]