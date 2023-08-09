
import time
from math import *
#import math
import os
import rcpy
import rcpy.motor as motor
from rcpy.motor import motor1,motor2,motor3
import rcpy.encoder as encoder
import rcpy.clock as clock
from pyPS4Controller.controller import Controller
from pyPS4Controller.event_mapping.DefaultMapping import DefaultMapping
import subprocess
import pyherkulex as hx
from serial import Serial
#import msvcrt#To catch events on keyboard


#Duty Time
DT = 0.02
DTus = DT*1000000


#max of Pulse Width Modulation
PWM_max=0.99

#1500 pulses/ rotation
#pi = math.pi   
COD = 1500/2.0/pi



#Function to avoid over value of pwm
def sature(v):
	if(v>PWM_max):
		return PWM_max
	if(v<-PWM_max):
		return -PWM_max
	return v

#Function to control with speed of the 4 wheels the duty cycle voltage of the motors		
class regulation(clock.Action):
	def __init__(self):
		#global speed in rad/s of the 4 wheels(for a robot with 4 wheels)

		#To gather the positions of the motors
		self.cod1=0
		self.cod2=0
		self.cod3=0
		#self.cod4=0
		
		#command in voltage duty cycle
		self.cmd1=0
		self.cmd2=0
		self.cmd3=0
		#self.cmd4=0

		self.err1=0
		self.err2=0
		self.err3=0
		#self.err4=0

		self.c_cod1=0
		self.c_cod2=0
		self.c_cod3=0
		#self.c_cod4=0

	
	
	def run(self):
		global w1,w2,w3
		t0 = time.clock_gettime(time.CLOCK_REALTIME)#get the real time
		#to enslave position
		self.c_cod1=self.c_cod1+w1*DT*COD
		self.c_cod2=self.c_cod2+w2*DT*COD
		self.c_cod3=self.c_cod3+w3*DT*COD
		#self.c_cod4=self.c_cod4+w4*DT*COD

		#Read Encodeur
		self.cod1=encoder.get(1)
		self.cod2=encoder.get(2)
		self.cod3=encoder.get(3)
		#self.cod4=encoder.get(4)
		#print("cod 1 2 and 3: ",self.cod1,self.cod2,self.cod3)#,self.cod4)

		self.err1=self.c_cod1-self.cod1
		self.err2=self.c_cod2-self.cod2
		self.err3=self.c_cod3-self.cod3
		#self.err4=self.c_cod4-self.cod4

		KP = 0.01#corrector proportionnal
		self.cmd1=KP*self.err1
		self.cmd2=KP*self.err2
		self.cmd3=KP*self.err3
		#self.cmd4=KP*self.err4

		#limit pwm command -1< cmd <1
		self.cmd1=sature(self.cmd1)
		self.cmd2=sature(self.cmd2)
		self.cmd3=sature(self.cmd3)
		#self.cmd4=sature(self.cmd4)
		#print("cmd1 :", self.cmd1, "cmd2 :",self.cmd2, "cmd3 :", self.cmd3)

		motor1.set(self.cmd1)
		motor2.set(self.cmd2)
		motor3.set(self.cmd3)
		#motor4.set(self.cmd4) #No need because we have just 3 wheels

		t1 = time.clock_gettime(time.CLOCK_REALTIME)#get the real time
		wait = DT -(t1-t0) 
		print("wait time in s is : ",wait)
		time.sleep(wait)#wait for the execution of the thread_regul


#Function to control the speed  of the 3 wheels with the speed of forward/backward(u)(m/s);Go_left/Go_right(v)(m/s);turn_no_clockwise(w)(rad/s)
def command(u,v,w):
	global w1,w2,w3,thread_regul
	w1=0
	w2=0
	w3=0
	#thread_regul.toggle()#unpause the thread_regul
	
	thread_regul.cod1=0
	thread_regul.cod2=0
	thread_regul.cod3=0

	thread_regul.cmd1=0
	thread_regul.cmd2=0
	thread_regul.cmd3=0

	thread_regul.err1=0
	thread_regul.err2=0
	thread_regul.err3=0

	thread_regul.c_cod1=0
	thread_regul.c_cod2=0
	thread_regul.c_cod3=0
	
	w1=(-(u)*math.sin(0)+v*math.cos(0)+1*w)/3
	w2=(-(u)*math.sin((2*3.14)/3)+v*math.cos((2*3.14)/3)+1*w)/3
	w3=(-(u)*math.sin((-2*3.14)/3)+v*math.cos((-2*3.14)/3)+1*w)/3

def stop_motors():
	
	global w1,w2,w3,thread_regul
	"""
	thread_regul.toggle()#unpause the thread_regul
	"""
	w1=0
	w2=0
	w3=0
	motor1.brake()
	motor2.brake()
	motor3.brake()
	
#BRAS###############################################################
#parametres du bras
l0 = 0.186
l1 = 0.195
l2 = 0.19
nvmax = 0.005 #modif max de (x,y) MGI
global x,y,dz
x=0.2
y=0.4
dz=6000

class arm_control(clock.Action):
	def __init__(self):
		global xn,yn,vup,vdown,vleft,vright,vstop,axe1,axe2,axe3
		vup = False
		vdown = False
		vleft = False
		vright = False
		vstop = False
		xn=0.2
		yn=0.4
		print("Position initiale")
		###########INIT BRAS###########################
		# Open the serial port (auto detected) with default baud rate 115200
		serial0 = hx.serial()
		# Broadcast reboot command to all servos connected to serial0
		# and light their LED in white
		broadcast_srv = hx.Servo(serial = serial0)
		broadcast_srv.reboot()
		broadcast_srv.led = hx.LED_WHITE

		# Create instances of servos
		axe1 = hx.Servo(0x02)
		axe2 = hx.Servo(0x03)
		axe3 = hx.Servo(0x05)

		# Enable control mode before sending control instructions
		axe1.mode = hx.MODE_CONTROL
		axe2.mode = hx.MODE_CONTROL
		axe3.mode = hx.MODE_CONTROL

		#Put braks in default position
		MGI(xn,yn,l0,l1,l2)
	def run(self):
		global x,y,xn,yn,vup,vdown,vleft,vright,vstop
		if vup:
			if yn < 0.9:
				yn += nvmax
			else:
				yn = 0.9
		if vdown:
			if yn > 0.2:
				yn -= nvmax
			else:
				yn = 0.2
		if vleft:
			if xn < 0.8:
				xn += nvmax
			else:
				xn = 0.8
		if vright:
			if xn > 0:
				xn -= nvmax
			else:
				xn = 0

		if xn != x or yn!=y:
			MGI(xn,yn,l0,l1,l2)
			x = xn
			y = yn
			#print('valeur de X = ',x,'\tvaleur de Y = ',y,'\n')
		if vstop:
			vstop = False
			axe1.control_stop()
			axe2.control_stop()
			axe3.control_stop() 	

def set_flag(flag_name,value):
	dz = 6000
	if(flag_name == (vdown or vright)):
		if (value > dz):
			flag_name = True
			return
		else:
			flag_name = False
			return
	elif(flag_name == (vup or vleft)):
		if (value < -dz):
			flag_name = True
			return
		else:
			flag_name = False
			return


#MGI_MATHS
def mgi_math(x,y,l1,l2,l0):
    y = y - l0
    if (sqrt(x**2+y**2) > l1+l2):
        return(False)

    teta2h =  -acos((x**2+y**2-(l1**2+l2**2))/(2*l1*l2))
            
    cteta1h = (x*(l1+l2*cos(teta2h))+y*l2*sin(teta2h))/(x**2+y**2)
    steta1h = (y*(l1+l2*cos(teta2h))-x*l2*sin(teta2h))/(x**2+y**2)

    teta1h = atan2(steta1h,cteta1h)

    return [teta1h,teta2h]

#MGI BRAS
def MGI(x,y,l0,l1,l2):
	global axe1,axe2,axe3
	MGI_MATH = mgi_math(x,y,l0,l1,l2)
	if MGI_MATH != False:
		# Conversion
		teta1 = MGI_MATH[0] * 180/pi
		teta2 = MGI_MATH[1] * 180/pi
		teta3 = -(teta2 + teta1) 

		#Actions des servos moteurs
		axe1.control_angle(124 - teta1,hx.LED_GREEN)
		axe2.control_angle(-7 + teta2,hx.LED_GREEN)
		axe3.control_angle(-57 + teta3,hx.LED_GREEN)
		#SLEEP TEMPS DE DEPLACEMENT
	else:
		print('POSITION LIMITE')
		#RESET DES SERVOS	
		#broadcast_srv.reboot()
		#broadcast_srv.led = hx.LED_WHITE


#####################################################################

"""
print("Commande de Jeu video normal, Z Q S D")
while(1):
	touche = msvcrt.getch()
	if touche =="z":
		command(60,0,0)#Go forward
	elif touche == "s":
		command(-60,0,0)#Go backward
	elif touche == "d":
		command(0,-60,0)#Go right
	elif touche == "q":
		command(0,60,0)#Go left
	else :
		print("Mauvaise touche")
	time.sleep(0.3)
	motor1.free_spin()
	motor2.free_spin()
	motor3.free_spin()
"""
   #/usr/local/lib/python3.5/dist-packages/rcpy-0.5.0-py3.5-linux-armv7l.egg/rcpy/clock.py"


class MyController(Controller):
	
	
	
	def __init__(self, **kwargs):
		Controller.__init__(self, **kwargs)
		global w1,w2,w3#,w4
		w1=0
		w2=0
		w3=0
		#w4=0
		
		global thread_regul
		#thread_regul=clock.Clock(regulation(),0.01)#Initialise a thread with the function regulation and the period of the thread is 0.01s
		#thread_regul.start()#launch the thread
		#Toggle pour etudier le thread_braks
		#thread_regul.toggle()#pause the thread_regul

		global thread_braks
		thread_braks=clock.Clock(arm_control(),0.01)#Initialise a thread with the function regulation and the period of the thread is 0.01s
		thread_braks.start()#launch the thread
		#thread_braks.toggle()
		#####################################################
		#Problemes avec vstop 
		
		
	def on_up_arrow_press(self):
		#Go forward
		command(100,0,0)


	def on_down_arrow_press(self):
		#Go backward
		command(-100,0,0)

	def on_right_arrow_press(self):
		#Go right
		command(0,-100,0)

	def on_left_arrow_press(self):
		#Go left
		command(0,100,0)

	def on_L1_press(self):
		#turn anti-clockwise
		command(0,0,-100)


	def on_R1_press(self):
		#turn clockwise
		command(0,0,100)


	def on_up_down_arrow_release(self):
		stop_motors()
		

	def on_left_right_arrow_release(self):
		stop_motors()
		
	
	def on_L1_release(self):
		stop_motors()
		
	
	def on_R1_release(self):
		stop_motors()
	    
	def on_R3_y_at_rest(self):
		global vstop
		vstop = True

	def on_R3_x_at_rest(self):
		global vstop
		vstop = True

	def on_R3_right(self,value):
		global vright,dz
		#set_flag(vright,value)
		if (value > dz):
			vright = True
		else:
			vright = False

	def on_R3_left(self,value):
		global vleft,dz
		#set_flag(vleft,value)
		if (value < -dz):
			vleft = True
		else:
			vleft = False

	def on_R3_down(self,value):
		global vdown,dz
		#set_flag(vdown,value)
		if (value > dz):
			vdown = True
		else:
			vdown = False

	def on_R3_up(self,value):
		global vup,dz
		#set_flag(vup,value)
		if (value < -dz):
			vup = True
		else:
			vup = False
			


	def on_options_press(self):  
		global xn,yn
		xn = 0.2
		yn=0.4
		print("Position initiale")



controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
controller.listen()

#/usr/local/lib/python2.7/dist-packages/pyPS4Controller/

