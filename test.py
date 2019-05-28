from flask import Flask, url_for, redirect
import click
app = Flask(__name__)
@app.route('/')
def index():
    return '<h1>Hello Flask!</h1>'

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