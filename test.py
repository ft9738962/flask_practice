from flask import Flask, url_for, redirect, render_template, Markup, flash, request
from flask_sqlalchemy import SQLAlchemy
import click, os, uuid
from forms import NewNoteForm, EditNoteForm, DeleteNoteForm

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY','secret string')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///'+os.path.join(app.root_path, 'data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 当使用flask shell启动python shell时，使用shell_context_processor注册的shell上下文处理函数都会自动执行
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Note=Note, Author=Author, Article=Article)

# 对于重复使用的命令，可以编写flask命令
@app.cli.command()
def initdb():
    db.create_all()
    click.echo('Initialized database.')

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)

    def __repr__(self):
        return f'<Note {self.body}>'

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    phone = db.Column(db.String(20))
    articles = db.relationship('Article')

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), index=True)
    body = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))

@app.route('/', methods=['GET'])
def index():
    form = DeleteNoteForm()
    notes = Note.query.all()
    return render_template('index.html', notes=notes, form=form)

@app.route('/new', methods=['GET', 'POST'])
def new_note():
    form = NewNoteForm()
    if form.validate_on_submit():
        body = form.body.data
        note = Note(body=body)
        db.session.add(note)
        db.session.commit()
        flash('Your note is saved.')
        return redirect(url_for('index'))
    return render_template('new_note.html', form=form)

@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    form = EditNoteForm()
    note = Note.query.get(note_id)
    if form.validate_on_submit():
        note.body = form.body.data
        db.session.commit()
        flash('The note has been updated')
        return redirect(url_for('index'))
    form.body.data = note.body
    return render_template('edit_note.html', form=form)

@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    form = DeleteNoteForm()
    note = Note.query.get(note_id)
    if form.validate_on_submit():
        db.session.delete(note)
        db.session.commit()
        flash('The note has been deleted')
        return redirect(url_for('index'))
    else:
        abort(400)
    return render_template('index')