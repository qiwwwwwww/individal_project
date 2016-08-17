from flask_wtf import Form
from wtforms import TextField, validators, StringField, SelectField

class DetailForm(Form):
	title = TextField('App Title', [validators.Length(min=1, max=100)])
	description = TextField('Description', [validators.length(min=1, max=50000)])
	category=SelectField('category', choices = [
		('Game','Game'), 
		('Social', 'Social'),
		('Lifestyle', 'Lifestyle'),
		('Education', 'Education'),
		('Communication', 'Communication'),
		('Sports', 'Sports'),
		('Music & Audio', 'Music & Audio'),
		('Shopping', 'Shopping'),
		('Productivity', 'Productivity'),
		('Business', 'Business'),
		('Medical', 'Medical'),
		('Tools', 'Tools'),
		('Transportation', 'Transportation'),
		('Weather', 'Weather'),
		('Travel & Local', 'Travel & Local'),
		('Photography', 'Photography'),
		('Personalization', 'Personalization'),
		('News & Magazines', 'News & Magazines'),
		('Books & Reference', 'Books & Reference'),
		('Health & Fitness', 'Health & Fitness')
		])