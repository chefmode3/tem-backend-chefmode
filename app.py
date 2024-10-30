from os.path import join, dirname
from dotenv import load_dotenv
import logging

from extractors import fetch_description

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

from flask import Flask, request
from flask_cors import CORS

from celery import Celery


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

celery = Celery(
    __name__,
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)


logging.getLogger('flask_cors').level = logging.DEBUG


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
        return {"content": res.result}