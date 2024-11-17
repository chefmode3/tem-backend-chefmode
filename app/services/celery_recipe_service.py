from app.extensions import db, celery
from app.models.celery_model import TaskResult
from celery.signals import task_prerun, task_postrun
from datetime import datetime
import time


class RecipeTaskService:
    @staticmethod
    def get_task_status(task_id):
        task_result = TaskResult.query.filter_by(task_id=task_id).first()
        if task_result:
            return task_result.to_dict()
        return None

    @staticmethod
    def create_task_result(task_id):
        task_result = TaskResult(task_id=task_id)
        db.session.add(task_result)
        db.session.commit()
        return task_result

    @staticmethod
    def update_task_result(task_id, status, result=None,  error=None):
        task_result = TaskResult.query.filter_by(task_id=task_id).first()
        if task_result:
            task_result.status = status
            task_result.result = result
            task_result.updated_at = datetime.utcnow()
            db.session.commit()
        return task_result


