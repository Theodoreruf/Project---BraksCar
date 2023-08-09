import pyherkulex as hx
import os
import time


# Open the serial port (auto detected) with default baud rate 115200
serial0 = hx.serial()

# Broadcast reboot command to all servos connected to serial0
# and light their LED in white
broadcast_srv = hx.Servo(serial = serial0)
broadcast_srv.reboot()
broadcast_srv.led = hx.LED_WHITE

# Create instances of servos
axe3 = hx.Servo(0x05)
axe1 = hx.Servo(0x02)
axe2 = hx.Servo(0x03)


print('axe 1: ', axe1.angle)
print('axe 2: ', axe2.angle)
print('axe 3: ', axe3.angle)

# Enable control mode before sending control instructions
axe1.mode = hx.MODE_CONTROL
axe2.mode = hx.MODE_CONTROL
axe3.mode = hx.MODE_CONTROL

#Actions des servos moteurs
axe3.control_angle(axe3.angle-10,hx.LED_GREEN)
time.sleep(2)
axe3.control_angle(axe3.angle+10,hx.LED_GREEN)
time.sleep(1)
print('SERVO AXE 1', axe1.position)
 	
    
