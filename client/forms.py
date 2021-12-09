from flask_wtf import FlaskForm
from wtforms import SubmitField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Length
from nohe.nohe import Operations

class UploadForm(FlaskForm):
	X = TextAreaField('Text X',
					validators=[DataRequired(), Length(min=1, max=1024, message='First text (1024 bytes max)')],
					render_kw={'class': 'form-control', 'rows': 2, 'columns': 20, 'placeholder': 'Type here from 1 to 1024 characters'}
					)
	Y = TextAreaField('Text Y',
					validators=[DataRequired(), Length(min=1, max=1024, message='Second text (1024 bytes max)')],
					render_kw={'class': 'form-control', 'rows': 2, 'columns': 20, 'placeholder': 'Type here from 1 to 1024 characters'}
					)
	operation = RadioField('Operation', 
					choices = [op.name for op in Operations],
					render_kw={'style': 'width:10%'})
	upload = SubmitField('Compute', 
					render_kw={'class': 'btn btn-primary btn-lg', 'style': 'width:100%'})
	result = TextAreaField('Result',
					render_kw={'class': 'form-control', 'rows': 2, 'columns': 20}
					)
	result_hex = TextAreaField('Result (hex)',
					render_kw={'class': 'form-control', 'rows': 2, 'columns': 20}
					)

	
