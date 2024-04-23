#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import datetime
import fingerprint as scanner
from fingerprint import finger
import adafruit_fingerprint
import aws
import classtime

colors = {"red": 0xFF0000, "green":0x00FF00, "blue": 0x0000FF, "off": 0x000000}
R = 13
G = 19
B = 26

motion_pin = 5


touch_pin = 25
tmp = 0

DETECTED = False	#used for printing 'Trying to detect finger'

def setup(Rpin, Gpin, Bpin):
	global pins
	global p_R, p_G, p_B
	GPIO.setwarnings(False)
	pins = {'pin_R': Rpin, 'pin_G': Gpin, 'pin_B': Bpin}
	GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by physical location
	for i in pins:    #Sets up LED pins
		GPIO.setup(pins[i], GPIO.OUT)   # Set pins' mode is output
		GPIO.output(pins[i], GPIO.HIGH) # Set pins to high(+3.3V) to off led
	GPIO.setup(motion_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    #Sets up Motion pin
	GPIO.setup(touch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Sets up touch pin
	
	p_R = GPIO.PWM(pins['pin_R'], 2000)  # set Frequece to 2KHz
	p_G = GPIO.PWM(pins['pin_G'], 1999)
	p_B = GPIO.PWM(pins['pin_B'], 5000)
	
	p_R.start(100)      # Initial duty Cycle = 0(leds off)
	p_G.start(100)
	p_B.start(100)

def map(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def off():
	GPIO.setmode(GPIO.BOARD)
	for i in pins:
		GPIO.setup(pins[i], GPIO.IN)   # Set pins' mode is output
		GPIO.output(pins[i], GPIO.HIGH)    # Turn off all leds

def setColor(col):   # For example : col = 0x112233
	R_val = (col & 0xff0000) >> 16
	G_val = (col & 0x00ff00) >> 8
	B_val = (col & 0x0000ff) >> 0

	R_val = map(R_val, 0, 255, 0, 100)
	G_val = map(G_val, 0, 255, 0, 100)
	B_val = map(B_val, 0, 255, 0, 100)
	
	p_R.ChangeDutyCycle(100-R_val)     # Change duty cycle
	p_G.ChangeDutyCycle(100-G_val)
	p_B.ChangeDutyCycle(100-B_val)
	

		
	
def get_time():
    time = datetime.datetime.now().strftime("%H:%M")	# returns time as string
    return time
    
def get_date():
    date = str(datetime.date.today())	# returns date as string
    return date
	
def CheckFingerprintErrors():
	if finger.read_templates() != adafruit_fingerprint.OK:
		raise RuntimeError("Failed to read templates")
		print("Fingerprint templates: ", finger.templates)
	if finger.count_templates() != adafruit_fingerprint.OK:
		raise RuntimeError("Failed to read templates")
		print("Number of templates found: ", finger.template_count)
	if finger.read_sysparam() != adafruit_fingerprint.OK:
		raise RuntimeError("Failed to get system parameters")

def loop():
	while True:
		global DETECTED
		CheckFingerprintErrors()
		
		if (not DETECTED):
			print("\nTrying to detect finger motion...")
			DETECTED = True

        
		if (0 == GPIO.input(motion_pin) or 1 == GPIO.input(touch_pin)):    # Detect Finger
			print ("\nDetected Barrier!")
			setColor(colors["blue"])   # Show that the device is on
			
			if (0 == GPIO.input(motion_pin)):	#publish motion_detected details
				motion_time = get_time()
				motion_date = get_date()
				class_session = classtime.getClass(motion_time)
				aws.publish_motion_detected(motion_time, motion_date, class_session)
			
			if (scanner.get_fingerprint()):    # Try test for fingerprint
				name = scanner.get_user(scanner.read_users(), finger.finger_id)	# Get Details
				scan_time = scanner.get_time()
				scan_date = scanner.get_date()
				class_session = classtime.getClass(scan_time)
				print("\n")
				print("Detected #", finger.finger_id, "with confidence", finger.confidence)
				print("Name:", name, "\nTime:", scan_time, "\nDate:", scan_date, "\nClass:", class_session)
				
				aws.publish_attendance(name, scan_time, scan_date, class_session)	# Publish Attendance Details
				
				setColor(colors["green"])
				time.sleep(2)
				DETECTED = False
			else:
				print("Finger not found")
				setColor(colors["red"])    # Alert On
				time.sleep(2)
				DETECTED = False
            
		
		if (1 == GPIO.input(motion_pin) and 0 == GPIO.input(touch_pin)):	#if not detected
			#print (".")
			setColor(colors["off"])
			time.sleep(.05)

def destroy():
	p_R.stop()
	p_G.stop()
	p_B.stop()
	off()
	GPIO.cleanup()

if __name__ == "__main__":
	try:
		setup(R, G, B)
		loop()
	except KeyboardInterrupt:
		destroy()
