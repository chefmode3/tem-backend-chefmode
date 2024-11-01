FROM python:3.9

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /app

COPY . .
CMD ["pip", "install", "greenlet"]

RUN pip install -r requirements.txt


