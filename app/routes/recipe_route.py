from flask_restx import Namespace, Resource
from flask import request, jsonify
from marshmallow import ValidationError

from app.serializers.utils_serialiser import convert_marshmallow_to_restx_model
from app.services.user_service import UserService
from app.serializers.recipe_serializer import (RecipeSchema, RecipeCreateSchema)
from flask_jwt_extended import jwt_required, get_jwt


auth_ns = Namespace('auth', description="user authentication")

