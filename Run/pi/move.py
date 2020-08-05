#!/usr/bin/env python3

import pigpio
from time import sleep

pi = None

WHEEL_PIN=18
BRAKE_PIN=17

# curl http://192.168.1.151:6890/move\?speed\=3\&time\=3\&braketime\=500

SPEEDS = [
	[0, 0],
	[500, 65],
	[600, 75],
	[1000, 128],
	[1000, 255],
	[1500, 128],
	[1750, 191],
	[2000, 255]
]

def move_can(runtime = 4, speed = 3, braketime = 5):
	global pi

	pi = pigpio.pi()

	pi.set_servo_pulsewidth(BRAKE_PIN, 1500)

	print('Starting at pulse width: ', {SPEEDS[int(speed)][0]}, 'and duty cycle: ', {SPEEDS[int(speed)][1]})
	# A period is the amount of time taken to complete a cycle
	pi.set_servo_pulsewidth(WHEEL_PIN, SPEEDS[int(speed)][0]) # safe clockwise
	# the amount of time the signal remains high in percentage with respect to the total time (Ton+Toff)
	pi.set_PWM_dutycycle(WHEEL_PIN, SPEEDS[int(speed)][1]) # Full on
	sleep(float(runtime))

	stop_can()
	
	print('Braking')

	# Almost 90
	pi.set_servo_pulsewidth(BRAKE_PIN, 1500)

	# 1500 is center, so to calculate your angle just subtract it (times 10) from 150. e.g: 1500 - (45 * 10) 
	pi.set_servo_pulsewidth(BRAKE_PIN, 900)
	sleep(float(braketime))

	pi.set_servo_pulsewidth(BRAKE_PIN, 1500)

	pi.stop()
	print('Done')

def stop_can():
	global pi

	print('Stopping')
	pi.set_servo_pulsewidth(WHEEL_PIN, 0)ß
	pi.set_PWM_dutycycle(WHEEL_PIN, 0) #  Off

if __name__ == '__main__':
    move_can()