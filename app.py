import os
from os.path import join, dirname
from dotenv import load_dotenv
import ssl

from app.extensions import mail
from app.config import Config
from extractors import fetch_description



from flask import Flask, request
from flask_cors import CORS
from celery import Celery


def create_app():
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    print(dotenv_path)
    print(os.getenv("TIME_ZONE"))
    app = Flask(__name__)

    app.config.from_object(Config)

    # Initialiser Flask-Mail
    mail.init_app(app)

    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    celery = Celery(
        __name__,
        broker=os.environ.get('REDIS_BROKER', ""),
        backend=os.environ.get('REDIS_BACKEND', ''),
        broker_use_ssl={
            'ssl_cert_reqs': ssl.CERT_NONE
        },
        redis_backend_use_ssl={
            'ssl_cert_reqs': ssl.CERT_NONE
        }

    )

    return app, celery


app, celery = create_app()


@celery.task(bind=True)
def call_fetch_description(self, data):
    return fetch_description(data)


@app.route("/get/recipe", methods=['POST'])
def image_extractor():
    data = request.json
    task = call_fetch_description.delay(data)

    return task.task_id


@app.route("/fetch_results", methods=['GET'])
def fetch_results():
    task_id = request.args.get("task_id")
    res = celery.AsyncResult(task_id)
    if res.state == 'PENDING':
        return {"status": "PENDING"}
    elif res.state == 'SUCCESS':
        return res.result
    elif res.state == 'FAILURE':
        return {"status": "FAILURE", "message": str(res.result)}
