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

from initializeState import *
from subscriber import *
from aldrin_code import *

class Search_Algorithm_For_QR_Code(smach.State):
	def __init__(self):
		print("Compiling Search Algorithm State")
		smach.State.__init__(self, outcomes = ['Search Algorithm Found QR Code'])
            	#Subscribe to all nodes that publish to smach
		self.sensors_sub = Subscribe_to('sensors2smach')
		self.lidar_sub = Subscribe_to('lidar2smach')
		self.cameras_sub = Subscribe_to('cameras2smach')
		self.controls_sub = Subscribe_to('controls2smach')
		self.counter = 0
		time.sleep(2)
		

	def execute(self, userdata):
		i = 0
		while ((i == 0) or (i>1) or (i<1)):
			print("")
			print("please input a number")
			print("1:Search Algorithm Found QR Code")
			i = input()
			if(i == 1):
				return 'Search Algorithm Found QR Code'

		

def code():
	rospy.init_node('sm')
	main = smach.StateMachine(outcomes = ['Gate_or_Post'])
	with main:
		smach.StateMachine.add('Search_Algorithm_For_QR_Code', Search_Algorithm_For_QR_Code(), transitions = {'Search Algorithm Found QR Code':'Gate_or_Post'})

	sis = smach_ros.IntrospectionServer('server' , main , '/tester')
	sis.start()
	outcome = main.execute()
	sis.stop()
	rospy.spin()

if __name__ == '__main__':
	code()
