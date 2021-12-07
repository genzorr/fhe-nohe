from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length
from nohe.nohe import Operations

class UploadForm(FlaskForm):
	X = StringField("Text X: ", validators=[DataRequired(), Length(min=1, max=1024, message="First text (1024 bytes max)")])
	# textX = RadioField('Text X type', choices=['string', 'bytes'])
	Y = StringField("Text Y: ", validators=[DataRequired(), Length(min=1, max=1024, message="Second text (1024 bytes max)")])
	# textY = RadioField('Text X type', choices=['string', 'bytes'])

	operation = RadioField('Operation', choices = [op.name for op in Operations])
	upload = SubmitField("Send")
