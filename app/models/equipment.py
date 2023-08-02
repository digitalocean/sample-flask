from app import db
from marshmallow import Schema, fields

class Equipment(db.Model):
    __tablename__ = 'equipment'
    idequipment = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    geo_location = db.Column(db.String(45))
    subsystem_idsubsystem = db.Column(db.Integer, db.ForeignKey('subsystem.idsubsystem'))
    subsystem = db.relationship('Subsystem', backref='equipment')

class EquipmentSchema(Schema):
    idequipment = fields.Integer(dump_only=True)
    name = fields.Str(required=True)
    geo_location = fields.Str()
    subsystem_idsubsystem = fields.Integer(required=True)
