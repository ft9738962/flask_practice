from flask import Flask, url_for, redirect, render_template, Markup, flash, request
from flask_sqlalchemy import SQLAlchemy
import click, os, uuid

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY','secret string')

db = SQLAlchemy(app)

app.config['UPLOAD_PATH'] = os.path.join(app.root_path, 'uploads')
app.config['ALLOWED_EXTENSIONS'] = ['png', 'jpg', 'jpeg', 'gif']
app.config['CKEDITOR_SERVE_LOCAL'] = True
app.config['CKEDITOR_FILE_UPLOADER'] = 'upload_for_ckeditor'

ckeditor = CKEditor(app)

user = {
    'username': 'Max Qiu',
    'bio': 'A boy who loves movies and music.'
}

movies = [
    {'name': 'My Neighbor Totoro', 'year': '1988'},
    {'name': 'Three Colours trilogy', 'year': '1993'},
    {'name': 'Forrest Gump', 'year': '1994'},
    {'name': 'Perfect Blue', 'year': '1997'},
    {'name': 'The Matrix', 'year': '1999'},
    {'name': 'Memento', 'year': '2000'},
    {'name': 'The Bucket list', 'year': '2007'},
    {'name': 'Black Swan', 'year': '2010'},
    {'name': 'Gone Girl', 'year': '2014'},
    {'name': 'CoCo', 'year': '2017'},
]

#利用globals添加全局参数
def bar():
    return 'I am bar.'
foo = 'I am foo.'
app.jinja_env.globals['bar'] = bar
app.jinja_env.globals['foo'] = foo
#自定义过滤器
def smiling(s):
    return s + ' :) '
app.jinja_env.filters['smiling'] = smiling
def baz(n):
    if n == 'baz':
        return True
    return False
app.jinja_env.tests['baz'] = baz
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'Error in the {getattr(form, field).label.text} field - {error}')
def random_filename(filename):
    ext = os.path.splitext(filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hello', defaults={'name': 'Human'})
@app.route('/hello/<name>')
def greet(name):
    return f'<h1>Hello,{name}</h1>'

@app.route('/greet')
def greet2():
    return redirect(url_for('greet', name='Jack'))

@app.cli.command()
def hello():
    click.echo('Hello, Man!')

@app.template_filter()
def musical(s):
    return s + Markup(' &#9835; ') #Markup提供转义功能

@app.route('/watchlist')
def watchlist():
    return render_template('watchlist.html', user=user, movies=movies)

@app.route('/flash')
def just_flash():
    flash('I am flash, who is looking for me? ')
    return redirect(url_for('index'))

@app.errorhandler(404) #错误处理装饰器需要传入错误代码
def page_not_found(e): #需要接受异常类作为参数
    return render_template('errors/404.html'), 404 #需要在返回值中标注HTTP状态码

@app.errorhandler(500)
def page_not_found(e):
    return render_template('errors/500.html'), 500

@app.route('/basic', methods=['GET', 'POST'])
def basic():
    basicform = BasicForm() # GET + POST
    '''
    以下使用validate_on_submit()对request进行验证
    其作用相当于 if request.method=='Post' and form.validate()的组合
    如果请求为POST类型，则验证数据类型，通过则获取用户名，如果请求为GET类型，则直接return渲染template
    '''
    if basicform.validate_on_submit(): # 当使用METHOD为POST,PUT,PATCH,DELETE时会验证
        username = basicform.username.data # 通常form.字段.data默认包含这个字段的数据
        flash(f'Welcome home, {username}!')
        return redirect(url_for('index'))
    flash_errors(basicform)
    return render_template('basic.html', form=basicform)

@app.route('/bootstrap', methods=['GET', 'POST']) #bootstrap风格表单
def bootstrap():
    bootform = BootForm()
    for attr in bootform: # 遍历表单里每个输入
        if attr.flags.required: # 如果某个输入有required标识
            attr.label.text += ' *' # 在渲染页面的label字符边上加上*号
    if bootform.validate_on_submit(): # 当使用METHOD为POST,PUT,PATCH,DELETE时会验证
        username = bootform.username.data
        flash(f'Welcome home, {username}!')
        return redirect(url_for('index'))
    flash_errors(bootform)
    return render_template('bootstrap.html', form=bootform)

@app.route('/upload', methods=['GET', 'POST']) #上传图片表单
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        f = form.photo.data
        filename = random_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        flash('Upload success.')
        session['filenames'] = [filename] #为兼容多文件传输
        return redirect(url_for('show_images'))
    flash_errors(form)
    return render_template('upload.html', form=form)

@app.route('/uploaded-images')
def show_images():
    return render_template('uploaded.html')

@app.route('/uploads/<path:filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/multi-upload', methods=['GET', 'POST'])
def multi_upload():
    form = MultiUploadForm()
    if request.method == 'POST':
        filenames = []
        #验证CSRF令牌
        try:
            validate_csrf(form.csrf_token.data)
        except ValidationError:
            flash('CSRF token error')
            return redirect(url_for('multi_upload'))
        #检查文件是否存在
        if 'photo' not in request.files:
            flash('This field is required')
            return redirect(url_for('multi_upload'))
        #循环保存文件
        for f in request.files.getlist('photo'):
            if f and allowed_file(f.filename):
                filename = random_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
                filenames.append(filename)
            else:
                flash('Invalid file type')
                return redirect(url_for('multi_upload'))
        flash('upload success')
        session['filenames'] = filenames
        return redirect(url_for('show_images'))
    return render_template('upload.html', form=form)

@app.route('/ckeditor', methods=['GET', 'POST'])
def integrate_ckeditor():
    form = RichTextForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        flash('Your post is published')
        return render_template('post.html', title=title, body=body)
    return render_template('ckeditor.html', form=form)

@app.route('/two-submits', methods=['GET', 'POST'])
def two_submits():
    form = NewPostForm()
    if form.validate_on_submit():
        if form.save.data:
            #save it...
            flash('You click the "Save" button')
        elif form.publish.data:
            #publish it...
            flash('You click the "Publish" button')
        return redirect(url_for('index'))
    return render_template('2submit.html', form=form)

@app.route('/multi-form', methods=['GET', 'POST'])
def multi_form():
    signin_form = SigninForm()
    register_form = RegisterForm()

    if signin_form.submit1.data and signin_form.validate():
        username = signin_form.username.data
        flash(f'{username}, you just submit the Signin Form.')
        return redirect(url_for('index'))

    if register_form.submit2.data and register_form.validate():
        username = register_form.username.data
        flash(f'{username}, you just sumbit the Register Form.')
        return redirect(url_for('index'))

    return render_template('2form.html', signin_form=signin_form, register_form=register_form)

@app.route('/multi-form-multi-view')
def multi_form_multi_view():
    signin_form = SigninForm2()
    register_form = RegisterForm2()
    return render_template('2form2view.html', signin_form=signin_form, register_form=register_form)

@app.route('/handle-signin', methods=['POST'])
def handle_signin():
    signin_form = SigninForm2()
    register_form = RegisterForm2()

    if signin_form.validate_on_submit():
        username = signin_form.username.data
        flash(f'{username}, you just submit the Signin Form.')
        return redirect(url_for('index'))
    flash_errors(signin_form)
    return render_template('2form2view.html', signin_form=signin_form, register_form=register_form)

@app.route('/handle-register', methods=['POST'])
def handle_register():
    signin_form = SigninForm2()
    register_form = RegisterForm2()

    if register_form.validate_on_submit():
        username = register_form.username.data
        flash(f'{username}, you just submit the Register Form.')
        return redirect(url_for('index'))
    flash_errors(register_form)
    return render_template('2form2view.html', signin_form=signin_form, register_form=register_form)