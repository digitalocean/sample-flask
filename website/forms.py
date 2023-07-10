from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField,
                     SubmitField, SelectField, TimeField, DateField, FileField)
from wtforms.validators import InputRequired


class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[InputRequired()])
    submit = SubmitField("Submit")


class OpenVoting(FlaskForm):
    round1 = BooleanField(label="Round 1 opened", false_values="Closed")
    submit_open_voting = SubmitField("Set")


class Candidate(FlaskForm):
    candidate_number = IntegerField("Candidate number")
    first_name = StringField("First name")
    last_name = StringField("Last name")


class SettingsBegin(FlaskForm):
    number_of_rounds = SelectField(label="Number of rounds", choices=[1, 2, 3])
    number_of_candidates = IntegerField('Number of candidates', validators=[InputRequired()])
    submit_settings_begin = SubmitField('Submit')


class SettingsRound(FlaskForm):
    active = BooleanField(label="Active?")
    scheme = SelectField(label="Voting scheme", choices=["yes-no", "score"])
    pass_limit = IntegerField('Passing limit')
    duration = TimeField(label="Duration per candidate", format='%M:%S')
    optional_piece = StringField("Optional piece")
    submit_round = SubmitField('Submit')


class ParticipantForm(FlaskForm):
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    birth_date = DateField(label="Date of Birth")
    email = StringField("E-mail")
    phone = IntegerField("Phone number")
    citizenship = StringField("Citizenship")
    street_number = StringField("Street and number")
    zip = IntegerField("ZIP")
    city = StringField("City")
    country = StringField("Country")
    photo = FileField()
    bio = TextAreaField(label="BIO")
    deposit = BooleanField("Deposit paid")
    in_full = BooleanField("Paid in full")
