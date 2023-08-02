from app import db
from marshmallow import Schema, fields
from .sensor import Sensor

# Define association table for many-to-many relationship
group_sensor_association = db.Table('group_has_sensor',
    db.Column('group_idgroup', db.Integer, db.ForeignKey('group.idgroup')),
    db.Column('sensor_idsensor', db.Integer, db.ForeignKey('sensor.idsensor'))
)

class Group(db.Model):
    __tablename__ = 'group'
    idgroup = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    description = db.Column(db.String(45))
    sensors = db.relationship('Sensor', secondary=group_sensor_association, backref='groups')

class GroupSchema(Schema):
    idgroup = fields.Integer(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
