#!/usr/bin/env python

import numpy as np
from numpy import linalg as LA

import rospy
from geometry_msgs.msg import Twist
from std_srvs.srv import Empty, SetBool, SetBoolRequest  
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from robotics_project.srv import MoveHead, MoveHeadRequest, MoveHeadResponse
from robotics_project.msg import PickUpPoseAction, PickUpPoseGoal, PickUpPoseActionGoal
from play_motion_msgs.msg import PlayMotionAction, PlayMotionGoal
from sensor_msgs.msg import JointState

from actionlib import SimpleActionClient
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from nav_msgs.msg import Odometry

from moveit_msgs.msg import MoveItErrorCodes
moveit_error_dict = {}
for name in MoveItErrorCodes.__dict__.keys():
    if not name[:1] == '_':
        code = MoveItErrorCodes.__dict__[name]
        moveit_error_dict[code] = name

class StateMachine(object):
    def __init__(self):
        
        self.node_name = "Student SM"
        
        # Access rosparams
        self.cmd_vel_top = rospy.get_param(rospy.get_name() + "/cmd_vel_topic")
        self.mv_head_srv_nm = rospy.get_param(rospy.get_name() + "/move_head_srv")
        self.pick_cube_up_service = rospy.get_param(rospy.get_name() + "/pick_srv")
        self.place_cube_up_service = rospy.get_param(rospy.get_name() + "/place_srv")

        self.pick_cube_up_action = rospy.get_param(rospy.get_name() + "/pickup_marker_pose")
        self.place_cube_up_action = rospy.get_param(rospy.get_name() + "/place_marker_pose")
        

        # Wait for services
        rospy.wait_for_service(self.mv_head_srv_nm, timeout=30)
        rospy.wait_for_service(self.pick_cube_up_service, timeout=30)
        rospy.wait_for_service(self.place_cube_up_service, timeout=30)
        rospy.wait_for_service(self.mv_head_srv_nm, timeout=30)
      
        # Cube pose
        cubepos = rospy.get_param(rospy.get_name() + '/cube_pose').split(",")

        self.cube_goal= PickUpPoseGoal()
        self.cube_goal.object_pose = PoseStamped()
        self.cube_goal.object_pose.pose.position.x = 0.502
        self.cube_goal.object_pose.pose.position.y = 0.0245718046511
        self.cube_goal.object_pose.pose.position.z = 0.82
        self.cube_goal.object_pose.pose.orientation.x = 0
        self.cube_goal.object_pose.pose.orientation.y = 0
        self.cube_goal.object_pose.pose.orientation.z = 0
        self.cube_goal.object_pose.pose.orientation.w = 1

        self.cube_goal.object_pose.header.frame_id = "base_footprint"

        # Subscribe to topics

 

        # Instantiate publishers
        self.cmd_vel_pub = rospy.Publisher(self.cmd_vel_top, Twist, queue_size=10)

        # Set up action clients
        # rospy.loginfo("%s: Name of picupo cube action %s",self.node_name, self.pick_cube_up_action)
        # self.pick_as = SimpleActionClient(self.pick_cube_up_action, PickUpPoseAction)
        # self.pick_as.wait_for_server()
        # rospy.loginfo("SSSSSSSSSSSSSSSSSSSsss")

        # rospy.loginfo("%s: Connected to pickup_marker_pose action server", self.node_name)



        rospy.loginfo("%s: Waiting for play_motion action server...", self.node_name)
        self.play_motion_ac = SimpleActionClient("/play_motion", PlayMotionAction)
        if not self.play_motion_ac.wait_for_server(rospy.Duration(1000)):
            rospy.logerr("%s: Could not connect to /play_motion action server", self.node_name)
            exit()
        rospy.loginfo("%s: Connected to play_motion action server", self.node_name)

        # Init state machine
        self.state = -1
        rospy.sleep(3)
        self.check_states()


    def check_states(self):

        while not rospy.is_shutdown() and self.state != 4:            
            # State 0: put arm in home position 
            if self.state == 0:
                try:
                    rospy.loginfo("%s: trying to set home postiotion", self.node_name)

                    goal = PlayMotionGoal()
                    goal.motion_name = 'home'
                    goal.skip_planning = True
                    self.play_motion_ac.send_goal(goal)

                    success_home = self.play_motion_ac.wait_for_result(rospy.Duration(2000.0))

                    if success_home:
                        rospy.loginfo("%s: arm in home postition", self.node_name)
                        self.state = 1
                    else:
                        rospy.loginfo("%s: arm in home postition - failed", self.node_name)
                        self.state = 0
                except:
                    rospy.loginfo("%s: error: arm in home position could not be put in the home postiotion", self.node_name)
                    self.state = 0
                rospy.sleep(1)

            # State 1:  search for Cube - in this case looking down 
            if self.state == 1:
                rospy.loginfo("%s: Looking down...", self.node_name)
                try:
                    rospy.loginfo("%s: Lowering robot head", self.node_name)
                    move_head_srv = rospy.ServiceProxy(self.mv_head_srv_nm, MoveHead)
                    move_head_req = move_head_srv("down")
                    
                    if move_head_req.success == True:
                        self.state = 2
                        rospy.loginfo("%s: Move head down succeeded!", self.node_name)
                    else:
                        rospy.loginfo("%s: Move head down failed!", self.node_name)
                        self.state = 1

                    rospy.sleep(3)
                
                except rospy.ServiceException, e:
                    print "Service call to move_head server failed: %s"%e

            # State 2:  try to achieve the pregrasp postition
            if self.state == 2:
                try:
                    goal = PlayMotionGoal()
                    goal.motion_name = "pregrasp"
                    goal.skip_planning = True
                    self.play_motion_ac.send_goal(goal)
                    success = self.play_motion_ac.wait_for_result()
                    if success:
                        self.state = 3
                    else:
                        self.state = 0
                except:
                    rospy.logerr("something went wrong pregrasp")
                rospy.sleep(1.0)

            # State 3: try to pickup cube
            if self.state == 3:
                rospy.loginfo("%s: try to pick up the cube now!", self.node_name)
                self.pick_as.send_goal_and_wait(self.cube_goal)
                rospy.loginfo("Done!")
                result = self.pick_as.wait_for_result()
                if result:
                    self.state = -1
                else:
                    self.state = -1


            # State -1: pass state
            if self.state == -1:
                pass
            # Error handling
            if self.state == 5:
                rospy.logerr("%s: State machine failed. Check your code and try again!", self.node_name)
                return

        rospy.loginfo("%s: State machine finished!", self.node_name)
        return


# import py_trees as pt, py_trees_ros as ptr

# class BehaviourTree(ptr.trees.BehaviourTree):

# 	def __init__(self):

# 		rospy.loginfo("Initialising behaviour tree")

# 		# go to door until at door
# 		b0 = pt.composites.Selector(
# 			name="Go to door fallback", 
# 			children=[Counter(30, "At door?"), Go("Go to door!", 1, 0)]
# 		)

# 		# tuck the arm
# 		b1 = TuckArm()

# 		# go to table
# 		b2 = pt.composites.Selector(
# 			name="Go to table fallback",
# 			children=[Counter(5, "At table?"), Go("Go to table!", 0, -1)]
# 		)

# 		# move to chair
# 		b3 = pt.composites.Selector(
# 			name="Go to chair fallback",
# 			children=[Counter(13, "At chair?"), Go("Go to chair!", 1, 0)]
# 		)

# 		# lower head
# 		b4 = LowerHead()

# 		# become the tree
# 		tree = pt.composites.Sequence(name="Main sequence", children=[b0, b1, b2, b3, b4])
# 		super(BehaviourTree, self).__init__(tree)

# 		# execute the behaviour tree
# 		self.setup(timeout=10000)
# 		while not rospy.is_shutdown(): self.tick_tock(1)


# class Counter(pt.behaviour.Behaviour):

# 	def __init__(self, n, name):

# 		# counter
# 		self.i = 0
# 		self.n = n

# 		# become a behaviour
# 		super(Counter, self).__init__(name)

# 	def update(self):

# 		# count until n
# 		while self.i <= self.n:

# 			# increment count
# 			self.i += 1

# 			# return failure :(
# 			return pt.common.Status.FAILURE

# 		# succeed after counter done :)
# 		return pt.common.Status.SUCCESS


# class Go(pt.behaviour.Behaviour):

# 	def __init__(self, name, linear, angular):

# 		# action space
# 		self.cmd_vel_top = rospy.get_param(rospy.get_name() + '/cmd_vel_topic')
# 		self.cmd_vel_pub = rospy.Publisher(self.cmd_vel_top, Twist, queue_size=10)

# 		# command
# 		self.move_msg = Twist()
# 		self.move_msg.linear.x = linear
# 		self.move_msg.angular.z = angular

# 		# become a behaviour
# 		super(Go, self).__init__(name)

# 	def update(self):

# 		# send the message
# 		rate = rospy.Rate(10)
# 		self.cmd_vel_pub.publish(self.move_msg)
# 		rate.sleep()

# 		# tell the tree that you're running
# 		return pt.common.Status.RUNNING


# class TuckArm(pt.behaviour.Behaviour):

# 	def __init__(self):

# 		# Set up action client
# 		self.play_motion_ac = SimpleActionClient("/play_motion", PlayMotionAction)

# 		# personal goal setting
# 		self.goal = PlayMotionGoal()
# 		self.goal.motion_name = 'home'
# 		self.goal.skip_planning = True

# 		# execution checker
# 		self.sent_goal = False
# 		self.finished = False

# 		# become a behaviour
# 		super(TuckArm, self).__init__("Tuck arm!")

# 	def update(self):

# 		# already tucked the arm
# 		if self.finished: 
# 			return pt.common.Status.SUCCESS
		
# 		# command to tuck arm if haven't already
# 		elif not self.sent_goal:

# 			# send the goal
# 			self.play_motion_ac.send_goal(self.goal)
# 			self.sent_goal = True

# 			# tell the tree you're running
# 			return pt.common.Status.RUNNING

# 		# if I was succesful! :)))))))))
# 		elif self.play_motion_ac.get_result():

# 			# than I'm finished!
# 			self.finished = True
# 			return pt.common.Status.SUCCESS

# 		# if I'm still trying :|
# 		else:
# 			return pt.common.Status.RUNNING
		


# class LowerHead(pt.behaviour.Behaviour):

# 	def __init__(self):

# 		# server
# 		mv_head_srv_nm = rospy.get_param(rospy.get_name() + '/move_head_srv')
# 		self.move_head_srv = rospy.ServiceProxy(mv_head_srv_nm, MoveHead)
# 		rospy.wait_for_service(mv_head_srv_nm, timeout=30)

# 		# execution checker
# 		self.tried = False
# 		self.tucked = False

# 		# become a behaviour
# 		super(LowerHead, self).__init__("Lower head!")

# 	def update(self):

# 		# try to tuck head if haven't already
# 		if not self.tried:

# 			# command
# 			self.move_head_req = self.move_head_srv("down")
# 			self.tried = True

# 			# tell the tree you're running
# 			return pt.common.Status.RUNNING

# 		# react to outcome
# 		else: return pt.common.Status.SUCCESS if self.move_head_req.success else pt.common.Status.FAILURE


	

if __name__ == "__main__":

	rospy.init_node('main_state_machine')
	try:
		#StateMachine()
		StateMachine()
	except rospy.ROSInterruptException:
		pass

	rospy.spin()
