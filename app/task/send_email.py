from flask import render_template

from flask_mailman import EmailMessage
from app.extensions import celery
from celery import current_task

@celery.task
def send_reset_email(email, body, subject,  recipient, type="html"):
    """Tâche asynchrone pour envoyer un e-mail de réinitialisation de mot de passe."""
    try:
        msg = EmailMessage(
            body=body,
            subject=subject,  # Assurez-vous que subject est sans retour à la ligne
            from_email=recipient,
            to=[email]
        )
        msg.content_subtype = type  # Définit le type de contenu, par exemple "html"

        # Envoi du message
        msg.send()
    except Exception as e:
        current_task.update_state(state="FAILURE", meta={"error": str(e)})
        raise