from flask_restx import fields


def convert_marshmallow_to_restx_model(api, schema):
    """
    Convertit un schéma Marshmallow en un modèle Flask-RESTX.
    """
    model = {}
    for field_name, field in schema.fields.items():
        field_type = type(field).__name__

        if field_type == "String":
            model[field_name] = fields.String(
                required=field.required, description=field.metadata.get("description", "")
            )
        elif field_type == "Email":
            model[field_name] = fields.String(
                required=field.required, description=field.metadata.get("description", "")
            )
        elif field_type == "Integer":
            model[field_name] = fields.Integer(
                required=field.required, description=field.metadata.get("description", "")
            )
        elif field_type == "Float":
            model[field_name] = fields.Float(
                required=field.required, description=field.metadata.get("description", "")
            )
        elif field_type == "Boolean":
            model[field_name] = fields.Boolean(
                required=field.required, description=field.metadata.get("description", "")
            )

    return api.model(schema.__class__.__name__, model)
