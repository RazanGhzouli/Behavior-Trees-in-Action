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

class Obstacle_Avoidance(smach.State):
	def __init__(self):
		print("Compiling Obstacle_Avoidance State")
		smach.State.__init__(self, outcomes = ['Avoided Obstacle'])
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
			print("1:Avoided Obstacle")
			i = input()
			if(i == 1):
				return 'Avoided Obstacle'

		

def code():
	rospy.init_node('sm')
	#main = smach.StateMachine(outcomes = ['Check CV for QR code', 'Check for Obstacle','Check if Checkpoint is gate or post'])
	with main:
		smach.StateMachine.add('Obstacle_Avoidance', Obstacle_Avoidance(), transitions = {'Avoided Obstacle':'Waypoint',})

	sis = smach_ros.IntrospectionServer('server' , main , '/tester')
	sis.start()
	outcome = main.execute()
	sis.stop()
	rospy.spin()

if __name__ == '__main__':
	code()
