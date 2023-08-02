from app import db
from marshmallow import Schema, fields

'''
sensor{
    idsensor :(int) ID do sensor (chave primária, gerado pelo banco de dados)
    id_influx_sensor :(str) ID do sensor no banco de dados InfluxDB (obrigatório)
    friendly_name :(str) Nome amigável do sensor (opcional)
    model_number :(str) Número do modelo do sensor (opcional)
    manufacturer :(str) Fabricante do sensor (opcional)
    installation_date :(datetime) Data de instalação do sensor (opcional)
    measurement_type :(str) Tipo de medição do sensor (opcional)
    measurement_unit :(str) Unidade de medição do sensor (opcional)
    measurement_unit_abbreviation :(str) Abreviação da unidade de medição do sensor (opcional)
    description :(str) Descrição do sensor (opcional)
    precision :(float) Precisão do sensor (opcional)
    max :(float) Valor máximo que o sensor pode medir (opcional)
    min :(float) Valor mínimo que o sensor pode medir (opcional)
    equipment_idequipment :(int) ID do equipamento associado a este sensor (chave estrangeira, opcional)
}
'''


class Sensor(db.Model):
    __tablename__ = 'sensor'
    idsensor = db.Column(db.Integer, primary_key=True)
    id_influx_sensor = db.Column(db.String(45), nullable=False)
    friendly_name = db.Column(db.String(45))
    model_number = db.Column(db.String(45))
    manufacturer = db.Column(db.String(45))
    installation_date = db.Column(db.DateTime)
    measurement_type = db.Column(db.String(45))
    measurement_unit = db.Column(db.String(45))
    measurement_unit_abbreviation = db.Column(db.String(45))
    description = db.Column(db.String(45))
    precision = db.Column(db.Numeric(10, 2))
    max = db.Column(db.Numeric(10, 2))
    min = db.Column(db.Numeric(10, 2))
    equipment_idequipment = db.Column(db.Integer, db.ForeignKey('equipment.idequipment'))
    equipment = db.relationship('Equipment', backref='sensors')

class SensorSchema(Schema):
    idsensor = fields.Integer(dump_only=True)
    id_influx_sensor = fields.Str(required=True)
    friendly_name = fields.Str()
    model_number = fields.Str()
    manufacturer = fields.Str()
    installation_date = fields.DateTime()
    measurement_type = fields.Str()
    measurement_unit = fields.Str()
    measurement_unit_abbreviation = fields.Str()
    description = fields.Str()
    precision = fields.Decimal(as_string=True)
    max = fields.Decimal(as_string=True)
    min = fields.Decimal(as_string=True)
    equipment_idequipment = fields.Integer(required=True)
