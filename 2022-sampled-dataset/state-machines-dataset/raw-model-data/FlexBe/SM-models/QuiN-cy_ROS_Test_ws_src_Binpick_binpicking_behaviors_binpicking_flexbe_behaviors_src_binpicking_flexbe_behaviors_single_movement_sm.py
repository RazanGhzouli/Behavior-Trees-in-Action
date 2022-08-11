#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################################
#               WARNING: Generated code!                  #
#              **************************                 #
# Manual changes may get lost if file is generated again. #
# Only code inside the [MANUAL] tags will be kept.        #
###########################################################

from flexbe_core import Behavior, Autonomy, OperatableStateMachine, ConcurrencyContainer, PriorityContainer, Logger
from flexbe_manipulation_states.srdf_state_to_moveit import SrdfStateToMoveit
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]

# [/MANUAL_IMPORT]


'''
Created on Sat Mar 14 2020
@author: Gerard Harkema
'''
class singlemovementSM(Behavior):
	'''
	Binpicking state machine
	'''


	def __init__(self):
		super(singlemovementSM, self).__init__()
		self.name = 'single movement'

		# parameters of this behavior

		# references to used behaviors

		# Additional initialization code can be added inside the following tags
		# [MANUAL_INIT]
		
		# [/MANUAL_INIT]

		# Behavior comments:



	def create(self):
		pick_group = 'manipulator'
		names = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint', 'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']
		gripper = 'epick_gripper_BasePickPointLink'
		gripper_device = '/dev/ttyUSB0'
		# x:1141 y:239, x:666 y:378
		_state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])
		_state_machine.userdata.pointcloud = []
		_state_machine.userdata.part_pose = []
		_state_machine.userdata.pick_configuration = []
		_state_machine.userdata.suction_cup_offset = 0.00
		_state_machine.userdata.rotation = 0
		_state_machine.userdata.move_group_prefix = ''
		_state_machine.userdata.move_group = "manipulator"
		_state_machine.userdata.ee_link = 'epick_gripper_BasePickPointLink'
		_state_machine.userdata.offset = 0
		_state_machine.userdata.pose = []
		_state_machine.userdata.tool_link = ''
		_state_machine.userdata.message = ''

		# Additional creation code can be added inside the following tags
		# [MANUAL_CREATE]
		
		# [/MANUAL_CREATE]


		with _state_machine:
			# x:292 y:60
			OperatableStateMachine.add('GoHomeStart',
										SrdfStateToMoveit(config_name='HomePos', move_group=pick_group, action_topic='/move_group', robot_name=""),
										transitions={'reached': 'finished', 'planning_failed': 'failed', 'control_failed': 'failed', 'param_error': 'failed'},
										autonomy={'reached': Autonomy.Off, 'planning_failed': Autonomy.Off, 'control_failed': Autonomy.Off, 'param_error': Autonomy.Off},
										remapping={'config_name': 'config_name', 'move_group': 'move_group', 'robot_name': 'robot_name', 'action_topic': 'action_topic', 'joint_values': 'joint_values', 'joint_names': 'joint_names'})


		return _state_machine


	# Private functions can be added inside the following tags
	# [MANUAL_FUNC]
	
	# [/MANUAL_FUNC]
