#!/usr/bin/env python3
import sys
import socket
import errno
from flask import Flask, request, render_template, flash, url_for, redirect
from forms import UploadForm
import nohe.nohe as nohe
from nohe.packet import Packet

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65534        # The port used by the server

# Initialize application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cb1e6f9701d72905e61638a00eda398f1f320ed3'

# Initialize coder
coder = nohe.Coder()

@app.route('/', methods=['POST', 'GET'])
def index():
	return render_template('index.html', title='Main Page')

@app.route('/upload', methods=['POST', 'GET'])
def upload():
	form = UploadForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			# Get X, Y, and operation type
			X = request.form['X']
			Y = request.form['Y']
			op = request.form['operation']
			
			# Encryption
			X = X.encode()
			Y = Y.encode()
			encX = coder.encode(X)
			encY = coder.encode(Y)
			result = None
			if op == 'XOR':
				result = 0
			elif op == 'AND':
				result = 1

			# Create packet
			packet = Packet(op, encX, encY)
			dataSend = packet.to_bytes()
			print(f'Source data: {X}, {Y}, needed result: {0}')
			print(f'Send data: {dataSend}')

			# Sent data to server
			dataRecv = None
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				sock.connect((HOST, PORT))
				sock.sendall(dataSend)
				flash('Request sent', category='success')
			except socket.error as e:
				flash('Cannot establish connection with server', category='error')
				print(f'Cannot establish connection with server, error: {e}')
			else:
				while True:
					try:
						dataRecv = sock.recv(Packet.maxSize)
					except socket.error as e:
						err = e.args[0]
						if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
							pass
						else:
							print(f'Socket error occured: {e}')
							sys.exit(1)
					else:
						if dataRecv and dataRecv != b'':
							print(f'Received data: {dataRecv}')
							break

			# Decrypt received data
			decXY = coder.decode(dataRecv)
			print(f'Decoded result: {decXY}')

		else:
			flash('Try again!', category='error')
			
	return render_template('upload.html', title='Upload', form=form)
	
	# if request.method == 'POST':
		# if len(request.form['number']) > 1:
		# 	flash('Successfully sent', category='success')
		# 	print(request.form['number'])
		# else:
		# 	flash('Try again!', category='error')

@app.errorhandler(404)
def pageNotFound(error):
	return render_template('error404.html', title='Page not found!'), 404

# Run clien application
app.run(debug=True)
