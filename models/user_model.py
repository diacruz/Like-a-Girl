from wtforms import Form, StringField, validators, PasswordField, TextAreaField
from bson.objectid import ObjectId

class LoginForm(Form):
    email = StringField('',
                        [validators.DataRequired(),
                         validators.Length(min=6, max=50)])
    password = PasswordField('',
                             [validators.DataRequired(),
                              validators.Length(min=8, max=50)])

class RegisterForm(Form):
    firstname = StringField('', [validators.Length(min=1, max=50)])
    lastname = StringField('', [validators.Length(min=1, max=50)])
    email = StringField('', [validators.Length(min=6, max=50), validators.Email()])
    password = PasswordField('',
                             [validators.DataRequired(),
                              validators.Length(min=8, max=50),
                              validators.EqualTo('confirm_password',
                                                 message='Passwords do not match')])
    confirm_password = PasswordField('', [validators.DataRequired()])

class Feed(Form):
    title = StringField('',  [validators.Length(min=1, max=100)])
    body = TextAreaField('',  [validators.Length(min=5, max=5000)])