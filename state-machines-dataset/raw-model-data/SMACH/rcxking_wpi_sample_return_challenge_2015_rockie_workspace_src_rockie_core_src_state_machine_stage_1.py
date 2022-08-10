#!/usr/bin/python

'''
State machine to run for stage 1.

RPI Rock Raiders
5/31/15

Last Updated: Bryant Pong: 6/11/15 - 2:03 PM
'''

# ROS Libraries:
import roslib
import rospy
import actionlib
from std_msgs.msg import String
from tf.transformations import quaternion_from_euler
from geometry_msgs.msg import Quaternion
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal, MoveBaseFeedback

# Finite State Machine Libraries
import smach
import smach_ros
from smach import StateMachine
from smach_ros import SimpleActionState

# For OpenCV:
import cv2
import numpy as np

# Operating System / Data Libraries:
import time

# Serial Messages for Services:
from serial_node.srv import * 

'''
Global Objects:
'''
lastState = 0

# Global flag for whether the sample has been found:
sampleFound = False  
paused = True    

'''
Pause State:
'''
class PauseState(smach.State):

	def __init__(self):
		smach.State.__init__(self, outcomes=["startupSequence", "egress", "transit", \
		"search", "searchTransit", "sampleRecog", "retSamp", "endTransit"])   				

		self.states = ["startupSequence", "egress", "transit", "search", \
		    "searchTransit", "sampleRecog", "retSamp", "endTransit"]
					
	def execute(self, userdata):
		global lastState, paused
		rospy.loginfo("Now in pause state.  Previous state is: " + str(lastState))

		rospy.wait_for_service("pauseservice")
		try:
			pause = rospy.ServiceProxy("pauseservice", Pause)
			x = pause(True)
		except rospy.ServiceException, e:
			print("Service call failed")

		while True:
			if paused == False:
				return self.states[lastState]
		return "startupSequence"
'''
This state performs system checks on the robot before beginning the run.   
'''
class StartupSequence(smach.State):
	def __init__(self):
		smach.State.__init__(self, outcomes=["done", "pause"])

	def execute(self, userdata):

		global lastState, paused
		rospy.loginfo("Executing Startup Sequence")	
		print("Turning on Amber Lights")
		rospy.wait_for_service("pauseservice")
		try:
			unpause = rospy.ServiceProxy("pauseservice", Pause)
			x = unpause(False)
		except rospy.ServiceException, e:
			rospy.loginfo("Service call failed: %s" % e)
		
		while True:
			if paused:
				print("startupsequence: Now going to pause state")
				lastState = 0
				return "pause"
		return "done"

class Egress(smach.State):
	def __init__(self):
		smach.State.__init__(self, outcomes=["transitEnter", "pause"])

	def execute(self, userdata):
		rospy.loginfo("Executing Egress")

		# Drive the robot off the starting platform:
		try:
			drive = rospy.ServiceProxy("driveservice", WheelVel) 
			x = drive(0.5, 0.5, 0.5)
			time.sleep(3)
			x = drive(0.0, 0.0, 0.0)			
		except rospy.ServiceException, e:
			rospy.loginfo("Service call failed: %s" % e)
						
		rospy.loginfo("Exiting off")  
		return "transitEnter"

class Transit(smach.State):
	def __init__(self):
		smach.State.__init__(self, outcomes=["searchEnter", "pause"])
		
	def execute(self, userdata):
		rospy.loginfo("Executing Transit")
					
		rospy.loginfo("Done executing Transit.  Now beginning search for object.")	
		return "searchEnter"
		
class Search(smach.State):
	def __init__(self):
		smach.State.__init__(self, outcomes=["searchTransitEnter", "pause"])

	def execute(self, userdata):
		rospy.loginfo("Executing Search")
		return "searchTransitEnter"

class SearchTransit(smach.State):
	def __init__(self):
		smach.State.__init__(self, outcomes=["sampleRecogEnter", "pause"])
	
	def execute(self, userdata):
		rospy.loginfo("Executing Search Transit")
		return "sampleRecogEnter"
		
class SampleRecognition(smach.State):
	def __init__(self):
		smach.State.__init__(self, outcomes=["sampleNotFound", "sampleFound", "pause"]) 			

	def execute(self, userdata):
		rospy.loginfo("Executing Sample Recognition")

		global sampleFound

		# Has the sample been found?
		if sampleFound:  
			return "sampleFound"
		else:
			return "sampleNotFound"

class RetrieveSample(smach.State):
	def __init__(self):
		smach.State.__init__(self, outcomes=["endTransitEnter", "pause"])
	
	def execute(self, userdata):
		rospy.loginfo("Executing Retrieve Sample")
		return "endTransitEnter"

class EndTransit(smach.State):
	def __init__(self):
		smach.State.__init__(self, outcomes=["pause", "end"])
	
	def execute(self, userdata):
		rospy.loginfo("Executing End Transit")
		return "end" 

def pauseCallback(data):
	rospy.loginfo("data.data: " + str(data.data))
	global paused
	if data.data == "yes":
		paused = True
	else:
		paused = False

def main():
	rospy.init_node('rockie_state_machine')
	rospy.Subscriber("pause", String, pauseCallback)
	sm = smach.StateMachine(outcomes=['complete'])
	with sm:
		smach.StateMachine.add("PAUSE", PauseState(), transitions={"startupSequence":"STARTUPSEQUENCE", "egress":"EGRESS", \
		    "transit":"TRANSIT", "search":"SEARCH", "searchTransit":"SEARCHTRANSIT", "sampleRecog":"SAMPLERECOGNITION", \
			"retSamp":"RETRIEVESAMPLE", "endTransit":"ENDTRANSIT"}) 
		smach.StateMachine.add("STARTUPSEQUENCE", StartupSequence(), transitions={"done":"complete", "pause":"PAUSE"})   
		smach.StateMachine.add("EGRESS", Egress(), transitions={"transitEnter":"TRANSIT", "pause":"PAUSE"})
		smach.StateMachine.add("TRANSIT", Transit(), transitions={"searchEnter":"SEARCH", "pause":"PAUSE"})
		smach.StateMachine.add("SEARCH", Search(), transitions={"searchTransitEnter":"SEARCHTRANSIT", "pause":"PAUSE"})
		smach.StateMachine.add("SEARCHTRANSIT", SearchTransit(), transitions={"sampleRecogEnter":"SAMPLERECOGNITION", "pause":"PAUSE"})
		smach.StateMachine.add("SAMPLERECOGNITION", SampleRecognition(), transitions={"sampleNotFound":"SEARCH","sampleFound":"RETRIEVESAMPLE", "pause":"PAUSE"})
		smach.StateMachine.add("RETRIEVESAMPLE", RetrieveSample(), transitions={"endTransitEnter":"ENDTRANSIT", "pause":"PAUSE"})
		smach.StateMachine.add("ENDTRANSIT", EndTransit(), transitions={"end":"complete", "pause":"PAUSE"})
	
	outcome = sm.execute()

if __name__ == "__main__":
	main()

