# -*- coding: utf-8 -*-
"""
Created on Wed Sep 29 08:52:25 2021

@author: meric.roselia
"""


# -*- coding: utf-8 -*-
from pyPS4Controller.controller import Controller


class MyController(Controller):
           
    
    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)


    def on_up_arrow_press(self):
        import subprocess
        commande = input()
        while(commande!='fin'):

            	if commande == 'avancer': 

                    
                    
            		subprocess.run(["./rob"])
                    
            		break

        
               
        
        
controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
controller.listen()

#/usr/local/lib/python2.7/dist-packages/pyPS4Controller/


