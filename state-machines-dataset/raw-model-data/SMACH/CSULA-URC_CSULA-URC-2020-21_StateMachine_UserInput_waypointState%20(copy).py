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

class Waypoint(smach.State):
	def __init__(self):
		print("Compiling WayPoint State")
		smach.State.__init__(self, outcomes = ['Found Obstacle','Completed Waypoint Navigation','Camera Found QR Code'])
            	#Subscribe to all nodes that publish to smach
		self.sensors_sub = Subscribe_to('sensors2smach')
		self.lidar_sub = Subscribe_to('lidar2smach')
		self.cameras_sub = Subscribe_to('cameras2smach')
		self.controls_sub = Subscribe_to('controls2smach')
		self.counter = 0
		time.sleep(2)
		

	def execute(self, userdata):
		# rospy.Subscriber("statemachine_control",Int16,callback)
		# pub = rospy.Publisher('waypointString',String,queue_size=10)
		# rospy.init_node('waypointState', anonymous=False)
		# rate = rospy.Rate(10)
		i = 0
		while ((i == 0) or (i>3) or (i<1)):			
			print("")
			print("please input a number")
			print("1:Found Obstacle -- 2:Completed Waypoint Navigation -- 3:Camera Found QR Code")
			i = input()
			if(i == 1):
				return 'Found Obstacle'
			elif(i == 2):
				return 'Completed Waypoint Navigation'
			elif(i == 3): 
				return 'Camera Found QR Code'
		

def code():
	rospy.init_node('sm')
	main = smach.StateMachine(outcomes = ['Check CV for QR code', 'Check for Obstacle','Check if Checkpoint is gate or post'])
	with main:
		smach.StateMachine.add('Waypoint', Waypoint(), transitions = {'Completed Waypoint Navigation':'Search Algorithm For QR Code',
								'Found Obstacle':'Obstacle_Avoidance',
								'Camera Found QR Code':'Gate_or_Post'})

	sis = smach_ros.IntrospectionServer('server' , main , '/tester')
	sis.start()
	outcome = main.execute()
	sis.stop()
	rospy.spin()

if __name__ == '__main__':
	code()
