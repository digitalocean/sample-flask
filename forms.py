from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, DateField
from wtforms.validators import InputRequired, Length


class LanguageForm(FlaskForm):
    language = StringField('Language', validators=[
        Length(min=5)])


class TranslationForm(FlaskForm):
    genre = SelectField('Genre', default='any')
    sl = SelectField('Source Language', default='any')
    tl = SelectField('Target Language', default='any')
    magazine = SelectField('Magazine', default='any')

    any_date = BooleanField('any date', default='checked')
    # after_date = DateField('after date')
    # before_date = DateField('before date')
    after_date = SelectField('After Date', default = 'any')
    before_date = SelectField('Before Date', default = 'any')
