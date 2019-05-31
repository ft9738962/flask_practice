from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message='名字不能为空')])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128, message='密码应为8至128位')])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')
