import RPi.GPIO as GPIO
import time
import threading

# Callback functions

callback_buttons = None

# GPIO Pinout

L1=11
L2=9

BS=10
BM=22
BC0=27
BC1=17

ECHO=3
TRIG=2

# Setup

def init(arg_cb):
	global callback_buttons
	callback_buttons = {	BS : arg_cb['BS'],
				BM : arg_cb['BM'],
				BC0 : arg_cb['BC0'],
				BC1 : arg_cb['BC1']}

	GPIO.setmode(GPIO.BCM)

	GPIO.setup(L1, GPIO.OUT)
	GPIO.setup(L2, GPIO.OUT)

	GPIO.setup(TRIG, GPIO.OUT)
	GPIO.setup(ECHO, GPIO.IN)
	
	GPIO.setup(BC0, GPIO.IN)
	GPIO.setup(BC1, GPIO.IN)
	GPIO.setup(BS, GPIO.IN)
	GPIO.setup(BM, GPIO.IN)

	GPIO.add_event_detect(BC0, GPIO.RISING, 
	callback=_wraper_buttons, bouncetime=300)
	GPIO.add_event_detect(BC1, GPIO.RISING, 
	callback=_wraper_buttons, bouncetime=300)
	GPIO.add_event_detect(BS, GPIO.RISING, 
	callback=_wraper_buttons, bouncetime=300)
	GPIO.add_event_detect(BM, GPIO.RISING, 
	callback=_wraper_buttons, bouncetime=300)

	# Waiting for sensors to settle
	time.sleep(2)

def clean():
	GPIO.cleanup()

# LED management

def turn_on_L1():
	GPIO.output(L1, True)

def turn_on_L2():
	GPIO.output(L2, True)

	
def turn_off_L1():
	GPIO.output(L1, False)

def turn_off_L2():
	GPIO.output(L2, False)

def _blink_both():
	turn_off_L1()
	turn_off_L2()

	for i in range(0,3):
		turn_on_L1()
		time.sleep(0.5)
		turn_off_L1()
		turn_on_L2()
		time.sleep(0.5)
		turn_off_L2()

def blink_both():
	t = threading.Thread(target=_blink_both)
	t.start()

# HC-SR04 management

def get_distance():
	while True:
		GPIO.output(TRIG, True)
		time.sleep(0.00001)
		GPIO.output(TRIG, False)
		
		pulse_start = None
		pulse_end = None
	
		start_polling = time.time()

		if GPIO.input(ECHO) == 1:
			print "ultrasonic sensor failure 0"
			time.sleep(5)
			continue

		restart = False
		while GPIO.input(ECHO) == 0:
			pulse_start=time.time()
			if pulse_start - start_polling > 5:
				print "ultrasonic sensor failure 1"
				restart = True
				break
		if restart:
			continue
		
		restart = False
		start_polling = time.time()
		while GPIO.input(ECHO) == 1:
			pulse_end=time.time()
			if pulse_end - start_polling > 5:
				print "ultrasonic sensor failure 2"
				restart = True
				break
		if restart:
			continue

		if pulse_end == None or pulse_start == None:
			time.sleep(3)
			print 'ultrasonic sensor failure 3'
			continue

		pulse_duration = pulse_end - pulse_start
		distance = pulse_duration*17150
		return distance

# Button management

ctl = False
def _wraper_buttons(channel):		
	global ctl
	global callback_buttons

	# If a thread is already up, just exit
	if ctl == True:
		return
	# Thread up flag
	ctl = True
	time.sleep(0.1)
	if GPIO.input(channel) == 1:
		# Call main button function
		
		callback_buttons[channel]()
		# Double while to be sure the GPIO is off
		while GPIO.input(channel) == 1:
			while GPIO.input(channel) == 1:
				time.sleep(0.1)
			time.sleep(0.1)
	# Release flag
	ctl = False
