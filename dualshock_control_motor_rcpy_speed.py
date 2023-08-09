
import time
import math
import rcpy
import rcpy.motor as motor
from rcpy.motor import motor1,motor2,motor3
import rcpy.encoder as encoder
import rcpy.clock as clock
from pyPS4Controller.controller import Controller
from pyPS4Controller.event_mapping.DefaultMapping import DefaultMapping
import subprocess
#import msvcrt#To catch events on keyboard


#Duty Time
DT = 0.02
DTus = DT*1000000


#max of Pulse Width Modulation
PWM_max=0.99

#1500 pulses/ rotation
pi = math.pi   
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
		global w1,w2,w3#,w4

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
		print("cod 1 2 and 3: ",self.cod1,self.cod2,self.cod3)#,self.cod4)

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
		print("cmd1 :", self.cmd1, "cmd2 :",self.cmd2, "cmd3 :", self.cmd3)

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

	thread_regul.toggle()#unpause the thread_regul
	
	
	w1=(-(u)*math.sin(0)+v*math.cos(0)+1*w)/3
	w2=(-(u)*math.sin((2*3.14)/3)+v*math.cos((2*3.14)/3)+1*w)/3
	w3=(-(u)*math.sin((-2*3.14)/3)+v*math.cos((-2*3.14)/3)+1*w)/3

	
	

	


def stop_motors():
	
	global thread_regul
	thread_regul.toggle()#unpause the thread_regul
	motor1.brake()
	motor2.brake()
	motor3.brake()
	
	

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
		thread_regul=clock.Clock(regulation(),0.01)#Initialise a thread with the function regulation and the period of the thread is 0.01s
		thread_regul.start()#launch the thread
		thread_regul.toggle()#pause the thread_regul
		
		
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
		command(0,0,100)


	def on_R1_press(self):
		#turn clockwise
		command(0,0,-100)


	def on_up_down_arrow_release(self):
		
		stop_motors()
		

	def on_left_right_arrow_release(self):
		
		stop_motors()
		
	
	def on_L1_release(self):
		stop_motors()
		
	
	def on_R1_release(self):
		stop_motors()
	


controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
controller.listen()

#/usr/local/lib/python2.7/dist-packages/pyPS4Controller/

