FROM python:3.9

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /app
RUN apt-get update -qq && apt-get install ffmpeg -y

COPY . .
CMD ["pip", "install", "greenlet"]

RUN pip install -r requirements.txt


