#!/usr/bin/python

'''
contingency.py - This script is our last resort for Phase 1.

It drives the robot forward, turns, and then aims to head back to home base.
'''

import rospy
import serial
import smach
import smach_ros
import time

from std_msgs.msg import String
from serial_node.srv import *

paused = True

lastState = 0
metersOffPlatform = 100
degreesToTurn = 100000000000000 
metersToSample = 1000 

class PauseState(smach.State):

	def __init__(self):
		smach.State.__init__(self, outcomes=["startupSequence", "forward", "turn", "lastForward"])

	def execute(self, userdata):
		global paused	
		rospy.loginfo("Now in paused state")
		rospy.wait_for_service("pauseservice")
		try:
			pause = rospy.ServiceProxy("pauseservice", Pause)
			x = pause(True)
		except rospy.ServiceException, e:
			print("Service call failed")

		while True:
			if paused == False:
				if lastState == 0:
					return "startupSequence"
				elif lastState == 1:
					return "forward"
				elif lastState == 2:
					return "turn"
				else:
					return "lastForward"
		return "forward"

class StartupSequence(smach.State):
	def __init__(self):
		smach.State.__init__(self, outcomes=["pause", "forward"])

	def execute(self, userdata):
		global paused
		rospy.loginfo("Now in startup sequence")
		rospy.wait_for_service("pauseservice")
		try:
			unpause = rospy.ServiceProxy("pauseservice", Pause)
			x = unpause(False)
		except rospy.ServiceException, e:
			print("Service call failed")

		rospy.wait_for_service("steer")
		try:
			turn = rospy.ServiceProxy("steer", Steer)
			x = turn(True)
		except rospy.ServiceException, e:
			print("Service call failed")

		if paused:
			lastState = 0
			return "pause"

		rospy.wait_for_service("steer")
		try:
			turn = rospy.ServiceProxy("steer", Steer)
			x = turn(False)
		except rospy.ServiceException, e:
			rospy.loginfo("Service call failed") 

		if paused:
			lastState = 0
			return "pause"

		return "forward"

class Forward(smach.State):
	def __init__(self):
		smach.State.__init__(self, outcomes=["pause","turn"])

	def execute(self, userdata):
		global paused, lastState, metersOffPlatform

		rospy.loginfo("Executing Forward")
		rospy.wait_for_service("pauseservice")

		try:
			unpause = rospy.ServiceProxy("pauseservice", Pause)
			x = unpause(False)
		except rospy.ServiceException, e:
			rospy.loginfo("Service call failed: s" % e)

		while metersOffPlatform > 0:
			try:
				rospy.wait_for_service("wheel_vel")
				drive = rospy.ServiceProxy("wheel_vel", WheelVel)
				x = drive(0.75, 0.75, 0.75, 0.75)
				time.sleep(0.01)		

				if paused:
					x = drive(0.0, 0.0, 0.0, 0.0)
					lastState = 1
					return "pause"
				metersOffPlatform -= 0.1
			except rospy.ServiceException, e:
				rospy.loginfo("Service call failed: %s" % e)

		try:
			drive = rospy.ServiceProxy("wheel_vel", WheelVel)
			x = drive(0.0, 0.0, 0.0, 0.0)
		except rospy.ServiceException, e:
			rospy.loginfo("Service call failed: %s" % e)
		return "turn"

class Turn(smach.State):
	def __init__(self):
		smach.State.__init__(self, outcomes=["pause", "lastForward"])

	def execute(self, userdata):
		global paused, lastState, degreesToTurn
		rospy.loginfo("Executing Turn")

		rospy.wait_for_service("pauseservice")
		try:
			unpause = rospy.ServiceProxy("pauseservice", Pause)
			x = unpause(False)		
		except rospy.ServiceException, e:
			rospy.loginfo("Service call failed: %s" % e)

		rospy.wait_for_service("steer")
		try:
			turn = rospy.ServiceProxy("steer", Steer)
			x = turn(True)
		except rospy.ServiceException, e:
			rospy.loginfo("Service call failed: %s" %  e)

		while degreesToTurn > 0:
			rospy.wait_for_service("wheel_vel")
			try:
				drive = rospy.ServiceProxy("wheel_vel", WheelVel)
				x = drive(0.75, 0.0, 0.75, 0.75) 
				time.sleep(0.01)

				if paused:
					x = drive(0.0, 0.0, 0.0, 0.0)
					lastState = 2
					return "pause"
				degreesToTurn -= 15
			except rospy.ServiceException, e:
				rospy.loginfo("Service call failed: %s" % e)

		rospy.wait_for_service("wheel_vel")
		try:
			drive = rospy.ServiceProxy("wheel_vel", WheelVel)
			x = drive(0.0, 0.0, 0.0, 0.0)
		except rospy.ServiceException, e:
			rospy.loginfo("Service call failed: %s" % e)

		return "lastForward"
						
class LastForward(smach.State):
	def __init__(self):
		smach.State.__init__(self, outcomes=["pause", "done"])

	def execute(self, userdata):
		global paused, lastState, metersToSample
		rospy.wait_for_service("pauseservice")
		rospy.loginfo("Executing LastForward")
		try:
			unpause = rospy.ServiceProxy("pauseservice", Pause)
			x = unpause(False)
		except rospy.ServiceException, e:
			rospy.loginfo("Service call failed: %s" % e)

		while metersToSample > 0:
			rospy.wait_for_service("wheel_vel")
			try:
				drive = rospy.ServiceProxy("wheel_vel", WheelVel)
				x = drive(0.75, 0.0, 0.75, 0.75)
				time.sleep(0.01)

				if paused:
					x = drive(0.0, 0.0, 0.0, 0.0)
					lastState = 3
					return "pause"
				metersToSample -= 0.01 
			except rospy.ServiceException, e:
				rospy.loginfo("Service call failed: %s" % e)
		
		rospy.wait_for_service("wheel_vel")
		try:
			stop = rospy.ServiceProxy("wheel_vel", WheelVel)
			x = stop(0.0, 0.0, 0.0, 0.0)
		except rospy.ServiceException, e:
			rospy.loginfo("Service call failed: %s" % e)
		return "done"
		
def pauseCallback(data):
        rospy.loginfo("data.data: " + str(data.data))
        global paused
        if data.data == "yes":
                paused = True
        else:
                paused = False

def main():
	rospy.init_node("rockie_state_machine")
	rospy.Subscriber("pause", String, pauseCallback)			 
	sm = smach.StateMachine(outcomes=['complete'])
	with sm:
		smach.StateMachine.add("PAUSE", PauseState(), transitions={"startupSequence":"STARTUPSEQUENCE", "forward":"FORWARD", "turn":"TURN", "lastForward":"LASTFORWARD"})
		smach.StateMachine.add("STARTUPSEQUENCE", StartupSequence(), transitions={"pause":"PAUSE", "forward":"FORWARD"})
		smach.StateMachine.add("FORWARD", Forward(), transitions={"pause":"PAUSE", "turn":"TURN"})
		smach.StateMachine.add("TURN", Turn(), transitions={"lastForward":"LASTFORWARD", "pause":"PAUSE"})
		smach.StateMachine.add("LASTFORWARD", LastForward(), transitions={"pause":"PAUSE", "done":"complete"})  

	outcome = sm.execute()


if __name__ == "__main__":
	main()



				 	  
