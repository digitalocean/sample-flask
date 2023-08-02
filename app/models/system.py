from app import db
from marshmallow import Schema, fields

class System(db.Model):
    __tablename__ = 'system'
    idsystem = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(45), nullable=False)
    Address = db.Column(db.String(45))
    Customer = db.Column(db.String(45))

class SystemSchema(Schema):
    idsystem = fields.Integer(dump_only=True)
    Name = fields.Str(required=True)
    Address = fields.Str()
    Customer = fields.Str()
