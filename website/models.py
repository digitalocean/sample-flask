from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


# model for users
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) #primary key - unique identifier
    email = db.Column(db.String(150), unique=True) #Unique specifies that only one such record can exist
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    notes = db.relationship('Note') #do your magic
    votes = db.relationship("Vote")


# model for notes
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now()) #f unc gets current date and time
    # foreign key references id to another database column - references to another record in this example to user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # this referrs to user who created the note


# model for votes
class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_number = db.Column(db.Integer)
    round_number = db.Column(db.Integer)
    score = db.Column(db.Integer)
    comment = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now()) # func gets current date and time
    # foreign key references id to another database column - references to another record in this example to user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # this referrs to user who created the note


class AuditionConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number_of_rounds = db.Column(db.Integer, default=1)
    current_round = db.Column(db.Integer, default=1)
    number_of_candidates = db.Column(db.Integer, default=1)


class ProductionConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    check_in = db.Column(db.Boolean, default=False)
    draw = db.Column(db.Boolean, default=False)


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_number = db.Column(db.Integer)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    round = db.Column(db.Integer, default=1)
    lot = db.Column(db.Boolean, default=False)


class SFOAParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    birth_date = db.Column(db.Date)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    citizenship = db.Column(db.String(100))
    street_number = db.Column(db.String(100))
    zip = db.Column(db.Integer)
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    checked_in = db.Column(db.Boolean, default=False)
    lot = db.Column(db.Boolean, default=False)
    photo = db.Column(db.String())
    bio = db.Column(db.String(10000))
    deposit = db.Column(db.Boolean, default=False)
    in_full = db.Column(db.Boolean, default=False)


class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    scheme = db.Column(db.String(100))
    pass_limit = db.Column(db.Float)
    anonymous = db.Column(db.Boolean)
    duration = db.Column(db.Time)
    active = db.Column(db.Boolean)
    ended = db.Column(db.Boolean)
    optional_piece = db.Column(db.String(200))


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate = db.Column(db.Integer)
    round = db.Column(db.Integer)
    score = db.Column(db.Float)
    passed = db.Column(db.Boolean)
