from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired, Length, ValidationError, Email

class NewNoteForm(FlaskForm):
    body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Save')

class EditNoteForm(NewNoteForm): #继承创造新表单类
    submit = SubmitField('Update')

class DeleteNoteForm(FlaskForm):
    submit = SubmitField('Delete')