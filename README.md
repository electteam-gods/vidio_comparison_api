# <p align="center"> ЦИФРОВОЙ ПРОРЫВ: ВСЕРОССИЙСКИЙ ХАКАТОН </p>
# <p align="center"> Поиск дубликатов видео </p>

# <p align="center"> ЭТО РЕПОЗИТОРИЙ СО ВСЕМИ ДЕТАЛЯМИ РЕАЛИЗАЦИИ НЕЙРОННОЙ МОДЕЛИ </p>

<p align="center">
<img width="800" height="400" alt="photo" src="https://github.com/NikitaGordievskiy/scalable_api_for_yappi_ai/blob/main/Group%201000010920.png">
</p> 

## Оглавление
1. [Задание](#1)
2. [Запуск](#12)
3. [Решение](#2)
4. [Практическая применимость](#3)
5. [Преимущества нашего решения](#4)
6. [Планы развития](#5)
7. [Стек](#6)
8. [Полезные ссылки](#7)

## <a name="1"> Задание </a>

Наша команда разработала сервис для решения задачи определения дубликатов в видео, публикуемых на платформе Yappi.

Проблематика решения состоит в том, что из-за большого количества видеоматериалов и разных способов модификации контента скоростной ручной поиск дублей практически невозможен. Однако эта задача является крайне важной, потому что дубликаты видео забирают себе охват с оригиналов, уменьшая статистику просмотров оригинала, что приведёт к тому, что авторы не будут размещать свой контент на платформе, которая не борется за их авторские права.

В качестве решения нами была представлена система с применением технологий искусственного интеллекта, включающая в себя API для проверки видео на предмет наличия дубликатов.

## <a name="12"> Запуск </a>

Модель была предварительно упакована в Docker-образ и доступна на Docker Hub: `docker.io/oleg36913/lcar_plate_app:v3`

Решение оформленно в виде стека Docker контейнеров, все сервисы поднимаются при помощи Docker Compose файлов:
1. `docker.compose.yml` - для прода

По шагам:
1. `git clone https://github.com/electteam-gods/scalable_api_for_yappi_ai.git - клонируем репозиторий
2. `cd scalable_api_for_yappi_ai` - переходим в папку с репозиторием
3. `docker compose up -f docker.compose.yml up -d` - запускаем весь стек
4. Ждём пару минут...
5. `echo "Enjoy!"`

P.S. В репозитории https://github.com/electteam-gods/scalable_api_for_yappi_ai.git организована очередь и Facade API для модели. Контейнер с моделью (docker.io/oleg36913/lcar_plate_app:v3) живёт независимо, от репозитория scalable_api_for_yappi_ai, и без труда может быть вырван и интегрирован в другую систему.

Проект без труда скейлится горизонтально, количество worker-нод можно скейлить 

## <a name="2">Решение </a>

Для качественного сравнения видео на плагиат мы используем:

1) Изменили цветовой формат BGR2Gray, затем Gray2RGB, после чего обрезали видео по краям.
2) Построили эмбеддинги видео с помощью модели TimeSFormer K600 и сохранили их в базу знаний.
3) На вход модели подаём сразу два варианата видео: исходное и отражённое. В случае если показатель схожести на исходном видео будет мал (<3%), а на отражённом существенно больше (>40%), то подтверждается гипотеза о том, что видео было отзеркалено и является плагиатом.
   
### Архетиктура решения

<img width="1200" height="500" alt="image" src="https://github.com/NikitaGordievskiy/scalable_api_for_yappi_ai/blob/main/Group%201000010919.png"> 

## <a name="3">Практическая применимость </a>

Практическая применимость решения заключается в простой интеграции нашего решения в большую задачу.

У нас обработка запроса происходит в 5 этапов:

1. Отправка "клиентом" запроса с ссылкой на изображение, которое предварительно было загружено на любое файловое хранилище, например S3-бакет.
2. Слой API создаёт задачу обработки фотографии и отправляет ее в очередь NEW_JOBS.
3. Worker'ы вытягивают из очереди NEW_JOBS новые задачи и начинают их обработку.
4. Завершив обработку Worker отправляет сообщение с результатом обработки номерного знака в очередь READY_JOBS.
5. API отдает клиенту выровненный под трафарет номер.

### Архетиктура системы

<img width="1200" height="500" alt="image" src="https://github.com/NikitaGordievskiy/scalable_api_for_yappi_ai/blob/main/scheme%201.png"> 

## <a name="4">Преимущества нашего решения </a>

1 Повышение точности решения сложных кейсов.

2 Высокая скорость принятия решения.

3 Масштабируемость.

4 Высокий процент попаданий при работе со сложными кейсами

5 Высокая точность установления дубликатов.

## <a name="5">Планы развития </a>

1 Повышение точности решения сложных кейсов.

2 Улучшение скорости работы алгоритма.

3 Система оповещений автора о наличии дубликата в видео.

4 Создание системы автоматического удаления дубликата.

## <a name="6">Стек </a>

<img src="https://github.com/devicons/devicon/blob/master/icons/python/python-original.svg" title="Python" alt="Puthon" width="40" height="40"/>&nbsp;
<img src="https://github.com/devicons/devicon/blob/master/icons/docker/docker-plain-wordmark.svg" title="Docker" alt="Puthon" width="40" height="40"/>&nbsp;
  <img src="https://github.com/devicons/devicon/blob/master/icons/pytorch/pytorch-original.svg" title="Pytorch" alt="Puthon" width="40" height="40"/>&nbsp;
  <img src="https://github.com/devicons/devicon/blob/master/icons/fastapi/fastapi-original.svg" title="FastApi" alt="Puthon" width="40" height="40"/>&nbsp;
  <img src="https://github.com/devicons/devicon/blob/master/icons/opencv/opencv-original.svg" title="OpenCV" alt="Puthon" width="40" height="40"/>&nbsp;
  <img src="https://github.com/celery/celery/blob/main/docs/images/celery_512.png" title="Celery" alt="Puthon" width="40" height="40"/>&nbsp;
  <img src="https://github.com/NikitaGordievskiy/scalable_api_for_yappi_ai/blob/main/image%204.png" title="Transformers" alt="Puthon" width="40" height="40"/>&nbsp;
  <img src="https://github.com/devicons/devicon/blob/6910f0503efdd315c8f9b858234310c06e04d9c0/icons/redis/redis-original-wordmark.svg" title="Redis" alt="Puthon" width="40" height="40"/>&nbsp;

## <a name="7">Полезные ссылки </a>

- [ссылка на код модели с комментариями](https://github.com/electteam-gods/vidio_comparison_api/tree/main/video_comparision_api)&nbsp;
- [ссылка на код реализации сервиса](https://github.com/electteam-gods/scalable_api_for_yappi_ai)&nbsp;
- [ссылка на скринкаст](https://disk.yandex.ru/d/lcg9v136wceEGw)&nbsp;




