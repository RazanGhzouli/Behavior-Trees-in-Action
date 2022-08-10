#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################################
#               WARNING: Generated code!                  #
#              **************************                 #
# Manual changes may get lost if file is generated again. #
# Only code inside the [MANUAL] tags will be kept.        #
###########################################################

from flexbe_core import Behavior, Autonomy, OperatableStateMachine, ConcurrencyContainer, PriorityContainer, Logger
from test_flexbe_states.get_pose import GetPoseState
from test_flexbe_states.planning_state import PlanningState
from test_flexbe_states.robot_move import RobotMoveState
from test_flexbe_states.ur5_ik import Ur5IkState
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]

# [/MANUAL_IMPORT]


'''
Created on Thu Jun 24 2021
@author: Andy Chien
'''
class test_behaviorsSM(Behavior):
	'''
	test behaviors
	'''


	def __init__(self):
		super(test_behaviorsSM, self).__init__()
		self.name = 'test_behaviors'

		# parameters of this behavior
		self.add_parameter('planner_action', 'robot_0/dcma_planner/move_group')
		self.add_parameter('robot_action', 'robot_0/arm_controller/follow_joint_trajectory')
		self.add_parameter('robot_id', 0)
		self.add_parameter('plan_mode', 'plan_only')

		# references to used behaviors

		# Additional initialization code can be added inside the following tags
		# [MANUAL_INIT]
		
		# [/MANUAL_INIT]

		# Behavior comments:



	def create(self):
		# x:152 y:279, x:775 y:86
		_state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])

		# Additional creation code can be added inside the following tags
		# [MANUAL_CREATE]
		
		# [/MANUAL_CREATE]


		with _state_machine:
			# x:126 y:73
			OperatableStateMachine.add('get_pose',
										GetPoseState(),
										transitions={'done': 'ur5_ik', 'fail': 'finished'},
										autonomy={'done': Autonomy.Off, 'fail': Autonomy.Off},
										remapping={'tar_trans': 'tar_trans', 'tar_rot': 'tar_rot'})

			# x:314 y:181
			OperatableStateMachine.add('move_robot',
										RobotMoveState(robot_action=self.robot_action),
										transitions={'done': 'get_pose', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'joint_trajectory': 'joint_trajectory'})

			# x:491 y:75
			OperatableStateMachine.add('plan',
										PlanningState(move_group='move_group', planner_action=self.planner_action, robot_id=self.robot_id, plan_mode=self.plan_mode),
										transitions={'reached': 'get_pose', 'planning_failed': 'failed', 'control_failed': 'failed', 'planned': 'move_robot'},
										autonomy={'reached': Autonomy.Off, 'planning_failed': Autonomy.Off, 'control_failed': Autonomy.Off, 'planned': Autonomy.Off},
										remapping={'joint_config': 'joint_values', 'joint_trajectory': 'joint_trajectory'})

			# x:307 y:4
			OperatableStateMachine.add('ur5_ik',
										Ur5IkState(),
										transitions={'done': 'plan', 'fail': 'failed'},
										autonomy={'done': Autonomy.Off, 'fail': Autonomy.Off},
										remapping={'tar_trans': 'tar_trans', 'tar_rot': 'tar_rot', 'joint_values': 'joint_values'})


		return _state_machine


	# Private functions can be added inside the following tags
	# [MANUAL_FUNC]
	
	# [/MANUAL_FUNC]
