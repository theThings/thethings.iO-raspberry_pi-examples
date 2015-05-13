#!/usr/bin/python

import ttgpio as ttg
import time
import threading
import thread
import ttrest
import subprocess

# Current machine state
state = 0

# Threading and root
root = threading.Event()
shutdown_request = False
memorize_request = False
password = "010"
input_pass = ""

# Constants
samp_num = 20
m = 30 # Default memorized distance

def bs():
	print 'BS'
	global shutdown_request
	if root.isSet():
		consume_root()
		shutdown_request = True

def bm():
	global memorize_request
	print 'BM'
	if root.isSet():
		consume_root()
		memorize_request = True
		
def bc0():
	print 'BC0'
	checkpass('0')

def bc1():
	print 'BC1'
	checkpass('1')

button_map = {	'BS': bs,
				'BM': bm,
				'BC0': bc0,
				'BC1': bc1}

# Check current read distance and memorized distance
def eqdistance(d, m): 
	rate = d/m
	return (rate > 0.90 and rate < 1.1)

# Root permission
def grant_root():
	global root
	root.set()

def consume_root():
	global root
	root.clear()

def checkpass(code):
	global input_pass
	global password
	input_pass = input_pass + code
	if len(input_pass) > len(password):
		input_pass = ""
	elif input_pass == password:
		input_pass = ""
		grant_root()
		
def update_reference_distance():
	ttg.blink_both()
	d = ttg.get_distance()
	time.sleep(0.2)
	d += ttg.get_distance()
	time.sleep(0.2)
	d += ttg.get_distance()
	m = d/3
	return m


time.sleep(30) # Wait for the system to start 
ttg.init(button_map)

# main loop
while True:

	# Check if user has pressed the shutdown button
	if shutdown_request:
		ttg.clean()
		subprocess.call(["shutdown", "-h", "now"])

	# Update reference distanc if requested
	if memorize_request:
		m = update_reference_distance()	
		memorize_request = False
		
	# Get distance from ultrasonic sensor
	d = ttg.get_distance()
	b = eqdistance(d, m)
	ttrest.ttwrite('Distance',str(d))

	# State 0 is listening for a distance lecture out of 
	# range. Once found, it will initialize some data for the
	# sate 1.
	if state == 0:
		print "i'm on state 0"
		if not b:
			state = 1
			samp_neg = 0 # negative samples
			samp_total = 0
	# On State 1, we will collect some more samples and then 
	# calculate an average of positives vs negatives. Regarding
	# the result, we will go back or forward.
	if state == 1:
		print "i'm on state 1"
		if not b:
			samp_neg+=1
		samp_total+=1

		if samp_total == samp_num:
			samp_rate = samp_neg / samp_total
			if samp_rate > 0.8:
				state = 2
			else:
				state = 0
	# On state 2, some time is given to the user to 
	# introduce a password. If anyone is entered, an 
	# alert will be sent. In any case, the next state
	# will be reached after the pass check.
	if state == 2:
		print "i'm on state 2"
		ttg.turn_on_L1()
		ttg.turn_on_L2()
		is_root = root.wait(20)
		ttg.turn_off_L1()
		ttg.turn_off_L2()
		if not is_root:
			print 'Alarm to TT'
			ttrest.ttwrite('AccesViolation','1')
		else:
			print 'Aborted alarm'
			ttrest.ttwrite('AbortedAlarm','1')
			ttg.blink_both()
			consume_root()
		state = 3
	# States 3 and 4 are equivalent to 0 and 2	
	if state == 3:
		print "i'm on state 3"
		if b:
			state = 4
			samp_pos = 0 # negative samples
			samp_total = 0
	if state == 4:
		print "i'm on state 4"
		if b:
			samp_pos+=1
		samp_total+=1

		if samp_total == samp_num:
			samp_rate = samp_pos / samp_total
			if samp_rate > 0.8:
				state = 0
			else:
				state = 3

	time.sleep(0.2)
