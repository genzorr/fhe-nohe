from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length

class UploadForm(FlaskForm):
	name = StringField("Your Name: ", validators=[DataRequired(), Length(min=1, max=15, message="Name up to 15 characters")])
	x = StringField("Text X: ", validators=[DataRequired(), Length(min=1, max=15, message="Number from 2 to 10 digits")])
	y = StringField("Text Y: ", validators=[DataRequired(), Length(min=1, max=15, message="Number from 2 to 10 digits")])
	choice = RadioField('Operation', choices = ['XOR', 'AND'])
	upload = SubmitField("Send")
