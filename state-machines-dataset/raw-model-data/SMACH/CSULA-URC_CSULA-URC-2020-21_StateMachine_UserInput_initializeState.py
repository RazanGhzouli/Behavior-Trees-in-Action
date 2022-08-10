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
from waypointState import *
from subscriber import *
from aldrin_code import *


class Initialize(smach.State):
	def __init__(self):
		print("Compiling Initialize State")
		smach.State.__init__(self, outcomes = ['Initialization Completed', 'Initialization Failed'])
            	#Subscribe to all nodes that publish to smach
		self.sensors_sub = Subscribe_to('sensors2smach')
		self.lidar_sub = Subscribe_to('lidar2smach')
		self.cameras_sub = Subscribe_to('cameras2smach')
		self.controls_sub = Subscribe_to('controls2smach')
		self.counter = 0
		time.sleep(2)

	def execute(self, userdata):
		self.counter = 0
		#Check if all nodes have published data
		sensors_data_sent = self.sensors_sub.was_data_sent()
		lidar_data_sent = self.lidar_sub.was_data_sent()
		cameras_data_sent = self.cameras_sub.was_data_sent()
		controls_data_sent = self.controls_sub.was_data_sent()

		print (sensors_data_sent, lidar_data_sent, cameras_data_sent, controls_data_sent)
		#If any of the nodes are not publishing, stay in this loop
		while ((sensors_data_sent == False) or (lidar_data_sent == False) 
			or (cameras_data_sent == False) or (controls_data_sent == False)):

			time.sleep(0.01)
			#continue checking if all nodes have published data
			sensors_data_sent = self.sensors_sub.was_data_sent()
			lidar_data_sent = self.lidar_sub.was_data_sent()
			cameras_data_sent = self.cameras_sub.was_data_sent()
			controls_data_sent = self.controls_sub.was_data_sent()
			print (sensors_data_sent, lidar_data_sent, cameras_data_sent, controls_data_sent)
			#If any nodes have failed to publsih after ~15 seconds, return failed
			if (self.counter > 1500):
				return 'Initialization Failed'
			self.counter = self.counter + 1

		#When all nodes are publishing data, return Finished
		return 'Initialization Completed'

def code():
	rospy.init_node('sm')
	main = smach.StateMachine(outcomes = ['Waypoint', 'Initialize'])
	with main:
		smach.StateMachine.add('Initialize', Initialize(), transitions = {'Initialization Completed':'Waypoint',
										'Initialization Failed':'Initialize'})


	sis = smach_ros.IntrospectionServer('server' , main , '/tester')
	sis.start()
	outcome = main.execute()
	sis.stop()
	rospy.spin()

if __name__ == '__main__':
	code()
