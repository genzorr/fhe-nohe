#!/usr/bin/env python3
import sys
import socket
import errno
from flask import Flask, request, render_template, flash, url_for, redirect
from .forms import UploadForm
import nohe.nohe as nohe
from nohe.packet import ClientPacket, ServerPacket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65534        # The port used by the server

# Initialize application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cb1e6f9701d72905e61638a00eda398f1f320ed3'
sock = None

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

			# Align texts
			max_len = max(len(X), len(Y))
			X += '0'*(max_len - len(X))
			Y += '0'*(max_len - len(Y))

			# Encryption
			X = X.encode()
			Y = Y.encode()
			coder = nohe.Coder()
			encX = coder.encode(X)
			encY = coder.encode(Y)
			# Calculate result
			result = None
			nohe_f = nohe.Functions(X, Y)
			if op == 'XOR':
				result = nohe_f.plain_xor()
			elif op == 'AND':
				result = nohe_f.plain_and()
			print(f'Source data: op = {op}, X = {X}, Y = {Y}, result = {result}')
			print(f'Encoded source: encX = {encX}, encY = {encY}')

			# Create packet
			packet = ClientPacket(op, encX, encY)
			dataSend = packet.to_bytes()
			# print(f'Sent packet: {dataSend}')

			# Sent data to server
			dataRecv = None
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				sock.connect((HOST, PORT))
				sock.sendall(dataSend)
				# flash('Request sent', category='success')
			except socket.error as e:
				flash('Cannot establish connection with server', category='error')
				print(f'Cannot establish connection with server, error: {e}')
			else:
				while True:
					try:
						dataRecv = sock.recv(ServerPacket.maxSize)
					except socket.error as e:
						err = e.args[0]
						if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
							pass
						else:
							print(f'Socket error occured: {e}')
							sys.exit(1)
					else:
						if dataRecv and dataRecv != b'':
							# print(f'Received packet: {dataRecv}')
							break

			# Extract received data
			packet = ServerPacket()
			Z1, Z2 = packet.from_bytes(dataRecv)
			print(f'Encoded result: Z1 = {Z1}, Z2 = {Z2}')

			# Decrypt received data
			decXY = coder.decode_res(Z1, Z2)
			print(f'Decoded result: {decXY}')

			if (result == decXY):
				print('Computation is valid')
				form.result.data = result.decode('utf-8')
				form.result_hex.data = result.hex()
			else:
				print('Computation is invalid')

			sock.close()
		else:
			flash('Error', category='error')
			
	return render_template('upload.html', title='Upload', form=form)

@app.errorhandler(404)
def pageNotFound(error):
	return render_template('error404.html', title='Page not found!'), 404

# Run client application
app.run(debug=True)
