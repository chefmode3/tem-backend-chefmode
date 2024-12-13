import logging

from flask import request
from flask_restx import Namespace, Resource
from marshmallow import ValidationError

from app.serializers.maillist_serializer import MailListSchema, MailListSerializerResponse
from app.serializers.utils_serialiser import convert_marshmallow_to_restx_model
from app.services.mail_service import MailService


maillist_ns = Namespace('save-mail', description='save user email')

maillistP_schema = MailListSchema()
maillistP_schema_response = convert_marshmallow_to_restx_model(maillist_ns, maillistP_schema)

logger = logging.getLogger(__name__)


@maillist_ns.route('/save')
class SaveMailResource(Resource):
    @maillist_ns.expect(maillistP_schema_response)
    @maillist_ns.response(201, 'Email successfully save')
    @maillist_ns.response(400, 'Validation Error')
    def post(self):

        try:
            data = maillistP_schema.load(request.get_json())
            email = data.get('email')
            if not email:
                logger.warning("Email field is missing.")
                return {'error': 'Email is required'}, 400

            mail_data, created = MailService.save_mail(email)
            if not created:
                return {'error': 'Email already exists or invalid'}, 400

            return MailListSerializerResponse().dump(mail_data), 201

        except ValidationError as err:
            logger.error(f"Validation error occurred: {str(err)}")
            return {'errors': err.messages}, 400

        except Exception as e:
            logger.exception("An unexpected error occurred.")
            return {'error': 'An unexpected error occurred', 'details': str(e)}, 400