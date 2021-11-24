from flask import Flask, request, render_template, flash, url_for, redirect
from forms import UploadForm
import socket
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65534        # The port used by the server


app = Flask(__name__)
app.config['SECRET_KEY'] = 'cb1e6f9701d72905e61638a00eda398f1f320ed3'


@app.route("/", methods=["POST", "GET"])
def index():
	return render_template('index.html', title="Main Page")


@app.route("/upload_number", methods=["POST", "GET"])
def upload_number():
	form = UploadForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			flash("Successfully sent!", category="success")
			client_number = request.form['number']
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
				s.connect((HOST, PORT))
				s.sendall(str(client_number).encode('utf8'))
			print(client_number)
		else:
			flash("Try again!", category="error")
			
	return render_template('upload_number.html', title="Upload", form=form)
	# if request.method == 'POST':
		# if len(request.form['number']) > 1:
		# 	flash("Successfully sent", category="success")
		# 	print(request.form['number'])
		# else:
		# 	flash("Try again!", category="error")


@app.errorhandler(404)
def pageNotFound(error):
	return render_template('error404.html', title='Page not found!'), 404


if __name__ == '__main__':
	app.run(debug=True)
