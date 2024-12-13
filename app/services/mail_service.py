import logging

from app.models.maillist import MailList
from app.extensions import db

logger = logging.getLogger(__name__)


class MailService:

    @staticmethod
    def save_mail(email: str):
        try:
            existing_mail = MailList.query.filter_by(mail=email).first()
            if existing_mail:
                logger.info(f"Email {email} already exists in the database.")
                return None, False

            new_mail = MailList(mail=email)
            db.session.add(new_mail)
            db.session.commit()
            logger.info(f"Email {email} successfully added to the database.")
            return new_mail, True

        except Exception as e:
            logger.error(f"Error saving email {email}: {str(e)}")
            db.session.rollback()
            return {'errors': {str(e)}}, False
