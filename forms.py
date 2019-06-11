from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired, Length, ValidationError, Email
from flask_ckeditor import CKEditorField

def is_12345678(form, field):
    '''自定义了字段值的判定方法，可以在定义字段时候用validators=[判定方法]
    这种验证方法称为全局验证，可以被多个字段复用
    但需要注意，这并不是常用形式
    '''
    if field.data != '12345678':
        raise ValidationError('Not 12345678')

def is_abcdefgh(message=None):
    '''就如上面提到的，常用形式为构建工厂函数，可以接受参数
    '''
    if message is None:
        message = 'Not abcdefgh'
    def _is_abcdefgh(form, field):
        if field.data != 'abcdefgh':
            raise ValidationError(message)
    return _is_abcdefgh

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message='名字不能为空')])
    password = PasswordField('Password', validators=[DataRequired(is_12345678), Length(8, 128, message='密码应为8至128位')])
    code = PasswordField('Code', validators=[is_12345678])
    vcode = PasswordField('Vcode', validators=[is_abcdefgh('dont mess with 12345678')])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')
    def validate_username(form, field): 
        '''将"validate_字段名"作为方法就可以自定义验证字段值
        这种验证只能对于某个字段使用，被称为行内验证(inline validator)
        '''
        if field.data != 'lemonade':
            raise ValidationError('Not lemonade!')

class UploadForm(FlaskForm):
    photo = FileField('Upload Image', 
    validators=[FileRequired(), FileAllowed(['jpg','jpeg','png','gif'],
    message='请提交jpg/jpeg/png/gif格式文件')])
    submit = SubmitField()

class MultiUploadForm(FlaskForm):
    photo = MultipleFileField('Upload Image', validators=[DataRequired()])
    submit = SubmitField()

class RichTextForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 50)])
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField('Publish')

class NewPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 50)])
    body = TextAreaField('Body', validators=[DataRequired()])
    save = SubmitField('Save')
    publish = SubmitField('Publish')

class SigninForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    submit1 = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 254)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    submit2 = SubmitField('Register')

class SigninForm2(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 24)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    submit = SubmitField()

class RegisterForm2(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 24)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 254)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    submit = SubmitField()