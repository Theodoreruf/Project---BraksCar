
import time
import rcpy.motor as motor
from rcpy.motor import motor1,motor2,motor3
from pyPS4Controller.controller import Controller
from pyPS4Controller.event_mapping.DefaultMapping import DefaultMapping
import subprocess


duty_motor_1 = 0
duty_motor_2 = 0
duty_motor_3 = 0




class MyController(Controller):

	def __init__(self, **kwargs):
		Controller.__init__(self, **kwargs)

	def on_up_arrow_press(self):
		
		duty_motor_2 = -1
		duty_motor_3 = 1
		motor2.set(duty_motor_2)
		motor3.set(duty_motor_3)



	def on_down_arrow_press(self):
		
		duty_motor_2 = 1
		duty_motor_3 = -1
		motor2.set(duty_motor_2)
		motor3.set(duty_motor_3)

	def on_right_arrow_press(self):
		
		duty_motor_1 = -0.8
		duty_motor_3 = 0.4
		duty_motor_2 = 0.4
		motor1.set(duty_motor_1)
		motor2.set(duty_motor_2)
		motor3.set(duty_motor_3)

	def on_left_arrow_press(self):
		
		duty_motor_1 = 0.8
		duty_motor_3 = -0.4
		duty_motor_2 = -0.4
		motor1.set(duty_motor_1)
		motor2.set(duty_motor_2)
		motor3.set(duty_motor_3)

	def on_L1_press(self):
		duty_motor_1 = -1
		duty_motor_3 = -1
		duty_motor_2 = -1
		motor1.set(duty_motor_1)
		motor2.set(duty_motor_2)
		motor3.set(duty_motor_3)

	def on_R1_press(self):
		duty_motor_1 = 1
		duty_motor_3 = 1
		duty_motor_2 = 1
		motor1.set(duty_motor_1)
		motor2.set(duty_motor_2)
		motor3.set(duty_motor_3)


	def on_up_down_arrow_release(self):
		
		motor1.set(0)
		motor2.set(0)
		motor3.set(0)

	def on_left_right_arrow_release(self):
		
		motor1.set(0)
		motor2.set(0)
		motor3.set(0)
	
	def on_L1_release(self):
		motor1.set(0)
		motor2.set(0)
		motor3.set(0)
	
	def on_R1_release(self):
		motor1.set(0)
		motor2.set(0)
		motor3.set(0)




controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
controller.listen()

#/usr/local/lib/python2.7/dist-packages/pyPS4Controller/
