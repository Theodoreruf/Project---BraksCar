# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 11:17:44 2021

@author: jeremy.grondin
"""
# -*- coding: utf-8 -*-
from pyPS4Controller.controller import Controller
import subprocess

flag = 0

class MyController(Controller):
           
    
    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)


    def on_up_arrow_press(self):
        flag=0
        while flag==0:
 
	        subprocess.run(["./rob_avancer_doss/rob_avancer"])
        
        def on_up_down_arrow_release(self):			
            flag=1
                
            
    
    def on_down_arrow_press(self):
           flag=0
           while flag==0:
	
               subprocess.run(["./rob_reculer_doss/rob_reculer"])
           def on_up_down_arrow_release(self):			
            flag=1
        
        
controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
controller.listen()

#/usr/local/lib/python2.7/dist-packages/pyPS4Controller/
