#-*-coding:utf-8-*-

from iwtform import Form
from wtforms import TextField, PasswordField, TextAreaField, validators
from wtforms.validators import Required, Length, InputRequired, EqualTo
from wtforms.fields import RadioField, IntegerField
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from sqlalchemy.orm import scoped_session, sessionmaker
from module.models import engine, User, Post, Term, Comment

class AdminLoginForm(Form):
    username = TextField('Username', [InputRequired(),Length(max=32)])
    password = PasswordField('Password', [InputRequired(),Length(min=6, max=60)])

class PostAddForm(Form):
    title = TextField('Title', [InputRequired(),Length(min=4)])
    parent = QuerySelectField(get_label='title', allow_blank=True, blank_text=u'Default')
    content = TextAreaField('Content', [InputRequired(),Length(min=1)])
    excerpt = TextAreaField('Except')
    date = TextField('Date')

class PageAddForm(Form):
    title = TextField('Name', [InputRequired(),Length(min=1, max=20)])
    parent = QuerySelectField(get_label='title', allow_blank=True, blank_text=u'Default')
    description = TextAreaField('Content')
    order = IntegerField('Order', [InputRequired()])

class TermAddForm(Form):
    name = TextField('Name', [InputRequired(),Length(min=1, max=20)])
    parent = QuerySelectField(get_label='name', allow_blank=True, blank_text=u'Default')
    description = TextAreaField('Description')

class UserEditForm(Form):
    displayname = TextField('Displayname', [InputRequired(),Length(min=2, max=32)])
    email = TextField('Email Address', [InputRequired(),Length(min=6,max=250)])
    password0 = PasswordField('Old Password', [InputRequired(),Length(min=6,max=32)])
    password1 = PasswordField('New Password', [InputRequired(),EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm', [InputRequired(),Length(min=6,max=32)])
