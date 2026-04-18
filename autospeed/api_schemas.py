from marshmallow import Schema, fields

class EntrySchema(Schema):
    id = fields.Int(required=True)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    status = fields.Str(required=True)
    created_at = fields.DateTime(required=True)

class EntryListResponse(Schema):
    data = fields.List(fields.Nested(EntrySchema), required=True)
    meta = fields.Dict(required=True)

class ErrorResponse(Schema):
    error = fields.Dict(required=True)