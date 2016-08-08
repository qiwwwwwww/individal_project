from flask_wtf import Form
from wtforms import TextField, validators, StringField, SelectField

class DetailForm(Form):
	title = TextField('App Title', [validators.Length(min=1, max=25)])
	description = TextField('Description', [validators.length(min=1, max=5000)])
	category=SelectField('category', choices = [('game','game'), ('social', 'social'),('lifestyle', 'lifestyle'),('Health & Fitness', 'Health & Fitness')])