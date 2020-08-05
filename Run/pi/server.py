#!/usr/bin/env python3

from flask import Flask, json, request
from move import move_can, stop_can

api = Flask(__name__)

@api.route('/move', methods=['GET'])
def move():
	runtime = request.args.get('time')
	speed = request.args.get('speed')
	braketime = request.args.get('braketime')
	move_can(runtime, speed, braketime)
	return 'True'

@api.route('/stop', methods=['GET'])
def stop():
	stop_can()
	return 'True'

if __name__ == '__main__':
    api.run(host='0.0.0.0', port=6890)