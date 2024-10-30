FROM python:3.9

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /app
#RUN brew install ffmpeg
#RUN brew install libsm6
#RUN brew install libxext6

COPY . .
CMD ["pip", "install", "greenlet"]

CMD pip install -r requirements.txt

