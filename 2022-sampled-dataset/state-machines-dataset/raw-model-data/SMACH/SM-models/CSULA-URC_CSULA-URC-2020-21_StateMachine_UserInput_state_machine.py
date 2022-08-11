#!/usr/bin/env python2

import roslib
import rospy
import smach
import smach_ros
import time

from std_msgs.msg import Int16
from std_msgs.msg import String

from aldrin_code.msg import cameras2smach
from aldrin_code.msg import controls2smach
from aldrin_code.msg import lidar2smach
from aldrin_code.msg import sensors2smach

#find a way to import all files
from subscriber import *
from initializeState import *
from waypointState import *
from obstacle_avoidanceState import *
from gate_or_postState import *
from search_algorithm_for_QR_codeState import *
from gate_codeState import *
from post_codeState import *
from mission_completeState import *


def code():
	rospy.init_node('sm')
	main = smach.StateMachine(outcomes = ['Done'])
	with main:
		# smach.StateMachine.add('Initialize', Initialize(), transitions = {'Initialization Completed':'Waypoint',
		# 								'Initialization Failed':'Initialize'})
	
	
		smach.StateMachine.add('Waypoint', Waypoint(), transitions = {'Completed Waypoint Navigation':'Search_Algorithm_For_QR_Code',
										'Found Obstacle':'Obstacle_Avoidance',
										'Camera Found QR Code':'Gate_or_Post'})

		smach.StateMachine.add('Obstacle_Avoidance', Obstacle_Avoidance(), transitions = {'Avoided Obstacle':'Waypoint'})

		smach.StateMachine.add('Gate_or_Post', Gate_or_Post(), transitions = {'Its a Gate!':'Gate_Code',
											'Its a Post!':'Post_Code'})

		smach.StateMachine.add('Search_Algorithm_For_QR_Code', Search_Algorithm_For_QR_Code(), transitions = {'Search Algorithm Found QR Code':'Gate_or_Post'})

		smach.StateMachine.add('Gate_Code', Gate_Code(), transitions = {'Gate Completed':'Mission_Complete'})

		smach.StateMachine.add('Post_Code', Post_Code(), transitions = {'Post Completed':'Mission_Complete'})

		smach.StateMachine.add('Mission_Complete', Mission_Complete(), transitions = {'Mission Completed':'Done',
												'Mission Not Completed':'Waypoint'})


		
	sis = smach_ros.IntrospectionServer('server' , main , '/tester')
	sis.start()
	outcome = main.execute()
	sis.stop()
	rospy.spin()

if __name__ == '__main__':
	code()
