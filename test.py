from flask import Flask, url_for, redirect, render_template, Markup, flash, request
from flask import send_from_directory, session
from forms import LoginForm, UploadForm
import click, os, uuid

app = Flask(__name__)
app.secret_key = 'secret string'

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

@app.template_filter()
def musical(s):
    return s + Markup(' &#9835; ') #Markup提供转义功能

@app.route('/watchlist')
def watchlist():
    return render_template('watchlist.html', user=user, movies=movies)

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
    form = LoginForm() # GET + POST
    '''
    以下使用validate_on_submit()对request进行验证
    其作用相当于 if request.method=='Post' and form.validate()的组合
    如果请求为POST类型，则验证数据类型，通过则获取用户名，如果请求为GET类型，则直接return渲染template
    '''
    if form.validate_on_submit(): # 当使用METHOD为POST,PUT,PATCH,DELETE时会验证
        username = form.username.data # 通常form.字段.data默认包含这个字段的数据
        flash(f'Welcome home, {username}!')
        return redirect(url_for('index'))
    return render_template('basic.html', form=form)

@app.route('/bootstrap', methods=['GET', 'POST']) #bootstrap风格表单
def bootstrap():
    form = LoginForm()
    for attr in form: # 遍历表单里每个输入
        if attr.flags.required: # 如果某个输入有required标识
            attr.label.text += ' *' # 在渲染页面的label字符边上加上*号
    if form.validate_on_submit(): # 当使用METHOD为POST,PUT,PATCH,DELETE时会验证
        username = form.username.data
        flash(f'Welcome home, {username}!')
        return redirect(url_for('index'))
    return render_template('bootstrap.html', form=form)

app.config['UPLOAD_PATH'] = os.path.join(app.root_path, 'uploads')

def random_filename(filename):
    ext = os.path.splitext(filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename

@app.route('/upload', methods=['GET', 'POST']) #上传图片表单
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        f = form.photo.data
        filename = random_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        flash('Upload success.')
        session['filenames'] = [filename] #为兼容多文件传输
        return redirect(url_for('get_file'))
    return render_template('upload.html', form=form)

@app.route('/uploads/<path:filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

