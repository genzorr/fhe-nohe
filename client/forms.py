from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class UploadForm(FlaskForm):
	name = StringField("Your Name: ", validators=[DataRequired(), Length(min=1, max=15, message="Name up to 15 characters")])
	number = StringField("Number: ", validators=[DataRequired(), Length(min=2, max=10, message="Number from 2 to 10 digits")])
	upload = SubmitField("Send")
