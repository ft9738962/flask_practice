from flask import Flask, url_for, redirect, render_template, Markup, flash
import click

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

def bar():
    return 'I am bar.'
foo = 'I am foo.'
app.jinja_env.globals['bar'] = bar
app.jinja_env.globals['foo'] = foo

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