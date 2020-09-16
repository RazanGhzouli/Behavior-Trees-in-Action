#!/usr/bin/env python
import py_trees as pt, py_trees_ros as ptr, rospy
from behaviours_student import *
from reactive_sequence import RSequence

import math
import actionlib
from geometry_msgs.msg import PoseStamped, Pose, PoseWithCovarianceStamped 
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal, MoveBaseActionGoal
from std_srvs.srv import Empty, SetBool, SetBoolRequest 
from gazebo_msgs.msg import ModelState
from gazebo_msgs.srv import SetModelState
from std_msgs.msg import Bool


class BehaviourTree(ptr.trees.BehaviourTree):
	def __init__(self):
		self.picked_up_cube_topic_name = rospy.get_name() + "/picked_up_cube_topic"
		self.place_pose_topic = rospy.get_param(rospy.get_name() + '/place_pose_topic')
		self.pickup_pose_topic = rospy.get_param(rospy.get_name() + '/pick_pose_topic')

		rospy.loginfo("Initialising behaviour tree")

		b0 = TuckArm()
		b1 = activate_localizator()  # activate global localizator
		b2 = pt.composites.Selector(
			name="Rotate for localization",
			children=[counter(70, "Rotated?"), go("Rotate!", 0, 1)])  # rotate for betteer localization
		b22 = respawn_cube()
		b3 = Navigate(self.pickup_pose_topic)
		# pickup
		b4 = LowerHead("Lower head!", "down")
		b5 = PickCube(self.picked_up_cube_topic_name)
		b6 = LowerHead("Rise head!", "up")

		b7 = Navigate(self.place_pose_topic)
		# place
		b8 = LowerHead("Lower head!", "down")
		b9 = PlaceCube()
		b10 = LowerHead("Rise head!", "up")
		# become the tree
		tree = RSequence(name="Main sequence", children=[b0, b1, b2, b22,  b3, b4, b5, b6, b7, b8, b9, b10])
		super(BehaviourTree, self).__init__(tree)

		# execute the behaviour tree
		rospy.sleep(5)
		self.setup(timeout=10000)
		while not rospy.is_shutdown(): self.tick_tock(1)	


### BEHAVIOURS

#### SERVICE global_localization
class activate_localizator(pt.behaviour.Behaviour):

	def __init__(self):

		# server
		rospy.wait_for_service('/global_localization', timeout=30)
		self.localize_srv = rospy.ServiceProxy('/global_localization', Empty)

		# execution checker
		self.activated = False

		# become a behaviour
		super(activate_localizator, self).__init__("Activate localizator!")

	def update(self):

		# try to tuck head if haven't already
		if not self.activated:

			# command
			x = self.localize_srv()
			print(x)
			self.activated = True

			# tell the tree you're running
			return pt.common.Status.SUCCESS

		# react to outcome
		else: return pt.common.Status.SUCCESS


#### ACTION SERVICE move_base
class Navigate(pt.behaviour.Behaviour):

	def __init__(self,pose_topic):
		
		self.pose_topic = pose_topic
		self.pose = None
		# Set up action client
		self.move_base_action = SimpleActionClient("/move_base", MoveBaseAction)

		# personal goal setting
		self.goal = MoveBaseGoal()

		# execution checker
		self.have_pose = False
		self.sent_goal = False
		self.finished = False

		# become a behaviour
		super(Navigate, self).__init__("Navigate!")

	def feedback_cb(self,feedback):
		position = feedback.base_position.pose.position
		orientation = feedback.base_position.pose.orientation
		delta_pos=math.hypot(self.pose.pose.position.x - position.x, self.pose.pose.position.y - position.y)
		delta_rot = math.hypot(self.pose.pose.orientation.z - orientation.z, self.pose.pose.orientation.w - orientation.w)
		if delta_pos < 0.09 and delta_rot < 0.05:
			self.finished = True
			self.move_base_action.cancel_all_goals()
		else:
			self.finished = False
			# rospy.loginfo("Position: %s. Orientation: %s", delta_pos, delta_rot )

	def done_cb(self, state, feedback):
			self.finished = True


	def update(self):

		# already tucked the arm
		if self.finished: 
			return pt.common.Status.SUCCESS
		
		# command to get the pose where to navigate to
		elif not self.have_pose:
			# Set up subscriber to get the pickup or place pose
			self.pose = rospy.wait_for_message(self.pose_topic, PoseStamped)
			self.have_pose = True
			return pt.common.Status.RUNNING

		elif not self.sent_goal:
			
			# send the goal
			self.goal = MoveBaseGoal(self.pose)
			# self.goal.target_pose = PoseStamped( self.pose)
			# self.goal.goal.target_pose = self.pose
			self.move_base_action.send_goal(self.goal, feedback_cb=self.feedback_cb , done_cb=self.done_cb)
			self.sent_goal = True

			# tell the tree you're running
			return pt.common.Status.RUNNING

		# if I'm still trying :|
		else:
			return pt.common.Status.RUNNING
			
### SIMPLE Services
class TuckArm(pt.behaviour.Behaviour): # put arm in home position

	def __init__(self):

		# Set up action client
		self.play_motion_ac = SimpleActionClient("/play_motion", PlayMotionAction)

		# personal goal setting
		self.goal = PlayMotionGoal()
		self.goal.motion_name = 'home'
		self.goal.skip_planning = True

		# execution checker
		self.sent_goal = False
		self.finished = False

		# become a behaviour
		super(TuckArm, self).__init__("Tuck arm!")

	def update(self):

		# already tucked the arm
		if self.finished: 
			return pt.common.Status.SUCCESS
		
		# command to tuck arm if haven't already
		elif not self.sent_goal:

			# send the goal
			self.play_motion_ac.send_goal(self.goal)
			self.sent_goal = True

			# tell the tree you're running
			return pt.common.Status.RUNNING

		# if I was succesful! :)))))))))
		elif self.play_motion_ac.get_result():

			# than I'm finished!
			self.finished = True
			return pt.common.Status.SUCCESS

		# if I'm still trying :|
		else:
			return pt.common.Status.RUNNING


class Running(pt.behaviour.Behaviour):
	def __init__(self):
		super(Running, self).__init__(name="running")
	
	def update(self):
		return pt.common.Status.RUNNING


class PickCube(pt.behaviour.Behaviour):
	def __init__(self, picked_up_cube_topic_name):
		self.pickService = rospy.get_param(rospy.get_name() + '/pick_srv')

		self.pickProxy = rospy.ServiceProxy(self.pickService, SetBool)
		self.pub = rospy.Publisher(picked_up_cube_topic_name, Bool, queue_size=10)
		# execution checker
		self.called_service = False
		self.finished = False
		
		super(PickCube, self).__init__("Pick Up Cube")
	def update(self):
		# try to tuck head if haven't already
		if not self.called_service:

			# command
			self.result = self.pickProxy(True)
			rospy.loginfo("result of the pick operation "+str(self.result.success))
			self.called_service = True

			# tell the tree you're running
			return pt.common.Status.RUNNING

		# react to outcome
		else: 
			#self.called_service = False
			#sb = SetBool()
			if self.result.success:				
				#sb.success = True
				self.pub.publish(Truee)
				return pt.common.Status.SUCCESS 
			else:
				#sb.success = False
				self.pub.publish(False)
				return pt.common.Status.FAILURE


class respawn_cube(pt.behaviour.Behaviour):

	def __init__(self):

		# server
		rospy.wait_for_service('/gazebo/set_model_state', timeout=30)
		self.respawn_cube_srv = rospy.ServiceProxy('/gazebo/set_model_state', SetModelState)

		# execution checker
		self.activated = False

		# become a behaviour
		super(respawn_cube, self).__init__("Respawn cube!")

	def update(self):

		# try to tuck head if haven't already
		if not self.activated:
			respawn_cube_srv_name = '/gazebo/set_model_state'
			
			rospy.wait_for_service(respawn_cube_srv_name, timeout=30)
			data = { 'model_name': 'aruco_cube', 'pose': { 'position': { 'x': -1.130530, 'y': -6.653650, 'z': 0.86250 }, 'orientation': {'x': 0, 'y': 0, 'z': 0, 'w': 1 } }, 'twist': { 'linear': {'x': 0 , 'y': 0, 'z': 0 } , 'angular': { 'x': 0, 'y': 0, 'z': 0 } } , 'reference_frame': 'map' }
			msg = ModelState()
			msg.model_name = data['model_name']
			pose = Pose()
			pose.position.x = data['pose']['position']['x']
			pose.position.y = data['pose']['position']['y']
			pose.position.z = data['pose']['position']['z']
			msg.pose = pose
			self.respawn_cube_srv(msg)

			# tell the tree you're running
			return pt.common.Status.SUCCESS

		# react to outcome
		else: return pt.common.Status.SUCCESS
		


class PlaceCube(pt.behaviour.Behaviour):
	def __init__(self):
		self.pickService = rospy.get_param(rospy.get_name() + '/place_srv')

		self.placeProxy = rospy.ServiceProxy(self.pickService, SetBool)

		# execution checker
		self.called_service = False
		self.finished = False
		
		super(PlaceCube, self).__init__("Place Cube")
	def update(self):
		# try to tuck head if haven't already
		if not self.called_service:

			# command
			self.result = self.placeProxy(True)
			rospy.loginfo("result of the place operation "+ str(self.result.success))
			self.called_service = True

			# tell the tree you're running
			return pt.common.Status.RUNNING

		# react to outcome
		else: return pt.common.Status.SUCCESS if self.result.success else pt.common.Status.FAILURE


class LowerHead(pt.behaviour.Behaviour):

	def __init__(self, name, type):

		# server
		mv_head_srv_nm = rospy.get_param(rospy.get_name() + '/move_head_srv')
		self.move_head_srv = rospy.ServiceProxy(mv_head_srv_nm, MoveHead)
		rospy.wait_for_service(mv_head_srv_nm, timeout=30)
		self.type = type
		# execution checker
		self.tried = False
		self.tucked = False

		# become a behaviour
		super(LowerHead, self).__init__(name)

	def update(self):

		# try to tuck head if haven't already
		if not self.tried:

			# command
			self.move_head_req = self.move_head_srv(self.type)
			self.tried = True

			# tell the tree you're running
			return pt.common.Status.RUNNING

		# react to outcome
		else: return pt.common.Status.SUCCESS if self.move_head_req.success else pt.common.Status.FAILURE


	### CONDITIONs

###reached pick position
class Pick_Pos_Condition(pt.behaviour.Behaviour):
	def callback(self, pose):
		self.position = pose.pose
		


	def __init__(self, pick_pose_topic):
		self.pick_pose_topic = pick_pose_topic
		self.amcl = '/amcl_pose'
		rospy.Subscriber(self.amcl, PoseWithCovarianceStamped, self.callback)
		self.postition = PoseStamped()

	def update(self):
		self.pose = rospy.wait_for_message(self.pick_pose_topic, PoseStamped)
		position = self.position.pose.position
		orientation = self.position.pose.orientation
		delta_pos=math.hypot(self.pose.pose.position.x - position.x, self.pose.pose.position.y - position.y)
		delta_rot = math.hypot(self.pose.pose.orientation.z - orientation.z, self.pose.pose.orientation.w - orientation.w)
		if delta_pos < 0.09 and delta_rot < 0.05:
			return pt.common.Status.SUCCESS 
		else:
			return pt.common.Status.FAILURE

###reached pick position
class Place_Pos_Condition(pt.behaviour.Behaviour):
	def callback(self, pose):
		self.position = pose.pose
		


	def __init__(self, place_pos_topic):
		self.place_pos_topic = place_pos_topic
		self.amcl = '/amcl_pose'
		rospy.Subscriber(self.amcl, PoseWithCovarianceStamped, self.callback)
		self.postition = PoseStamped()

	def update(self):
		self.pose = rospy.wait_for_message(self.place_pos_topic, PoseStamped)
		position = self.position.pose.position
		orientation = self.position.pose.orientation
		delta_pos=math.hypot(self.pose.pose.position.x - position.x, self.pose.pose.position.y - position.y)
		delta_rot = math.hypot(self.pose.pose.orientation.z - orientation.z, self.pose.pose.orientation.w - orientation.w)
		if delta_pos < 0.09 and delta_rot < 0.05:
			return pt.common.Status.SUCCESS 
		else:
			return pt.common.Status.FAILURE

###cube picked
class cube_picked(pt.behaviour.Behaviour):
	def callback(self, setBool):
		self.cube_picked = setBool
	
	def __init__(self, cube_picked_topic_name):
		self.cube_picked = False
		#does this one have to be called, the main already does that
		rospy.init_node('node_name')

		rospy.Subscriber(cube_picked_topic_name, Bool, self.callback)
	
	def update(self):
		if self.cube_picked:
			return pt.common.Status.SUCCESS
		else:
			return pt.common.Status.FAILURE







if __name__ == "__main__":


	rospy.init_node('main_state_machine')
	try:
		BehaviourTree()
	except rospy.ROSInterruptException:
		pass

	rospy.spin()