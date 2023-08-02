from app import db
from marshmallow import Schema, fields

class Subsystem(db.Model):
    __tablename__ = 'subsystem'
    idsubsystem = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    system_idsystem = db.Column(db.Integer, db.ForeignKey('system.idsystem'))
    system = db.relationship('System', backref='subsystems')

class SubsystemSchema(Schema):
    idsubsystem = fields.Integer(dump_only=True)
    name = fields.Str(required=True)
    system_idsystem = fields.Integer(required=True)
