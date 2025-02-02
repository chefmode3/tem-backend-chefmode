import os
from os.path import join, dirname
from dotenv import load_dotenv
import logging
import ssl
from extractors import fetch_description


from flask import Flask, request
from flask_cors import CORS

from celery import Celery


logger = logging.getLogger(__name__)


def create_app():
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    logger.info(dotenv_path)
    logger.info(os.getenv("TIME_ZONE"))
    app = Flask(__name__)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    celery = Celery(
        __name__,
        broker="rediss://:p001004ca65035c7d381457ecf466defc3710bc746fcca3d97b41b0184759034c@ec2-98-84-198-124.compute-1.amazonaws.com:13919/0",
        backend="rediss://:p001004ca65035c7d381457ecf466defc3710bc746fcca3d97b41b0184759034c@ec2-98-84-198-124.compute-1.amazonaws.com:13919/0",
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
        logger.info("Failure Message:", res.result)
        return {"status": "FAILURE"}
