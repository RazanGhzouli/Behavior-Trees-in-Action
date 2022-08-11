#!/usr/bin/env python2

import roslib
import rospy
import smach
import smach_ros
import time

from aldrin_code.msg import cameras2smach
from aldrin_code.msg import controls2smach
from aldrin_code.msg import lidar2smach
from aldrin_code.msg import sensors2smach

from subscriber import *


class Gate_or_Post(smach.State):
	def __init__(self):
		print("Compiling Gate or Post State")
		smach.State.__init__(self, outcomes = ['Its a Gate!','Its a Post!'])
            	#Subscribe to all nodes that publish to smach
		self.sensors_sub = Subscribe_to('sensors2smach')
		self.lidar_sub = Subscribe_to('lidar2smach')
		self.cameras_sub = Subscribe_to('cameras2smach')
		self.controls_sub = Subscribe_to('controls2smach')
		self.counter = 0
		time.sleep(2)
		

	def execute(self, userdata):
		i = 0
		while ((i == 0) or (i>2) or (i<1)):
			print("")
			print("please input a number")
			print("1:Its a Gate! -- 2:Its a Post!")
			i = input()
			if(i == 1):
				return 'Its a Gate!'
			elif(i == 2):
				return 'Its a Post!'
		

def code():
	rospy.init_node('sm')
	main = smach.StateMachine(outcomes = ['Gate_Code','Post_Code'])
	with main:
		smach.StateMachine.add('Gate_or_Post', Gate_or_Post(), transitions = {'Its a Gate!':'Gate_Code',
										'Its a Post!':'Post_Code',})

	sis = smach_ros.IntrospectionServer('server' , main , '/tester')
	sis.start()
	outcome = main.execute()
	sis.stop()
	rospy.spin()

if __name__ == '__main__':
	code()
