#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################################
#               WARNING: Generated code!                  #
#              **************************                 #
# Manual changes may get lost if file is generated again. #
# Only code inside the [MANUAL] tags will be kept.        #
###########################################################

from flexbe_core import Behavior, Autonomy, OperatableStateMachine, ConcurrencyContainer, PriorityContainer, Logger
from flexbe_states.wait_state import WaitState
from flexbe_manipulation_states.srdf_state_to_moveit import SrdfStateToMoveit
from flexbe_states.publisher_bool_state import PublisherBoolState
from flexbe_states.subscriber_state import SubscriberState
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]

# [/MANUAL_IMPORT]


'''
Created on Thu Jun 10 2021
@author: q / y
'''
class AGVPlaceSM(Behavior):
	'''
	plaatst object op agv
	'''


	def __init__(self):
		super(AGVPlaceSM, self).__init__()
		self.name = 'AGV Place'

		# parameters of this behavior

		# references to used behaviors

		# Additional initialization code can be added inside the following tags
		# [MANUAL_INIT]
		
		# [/MANUAL_INIT]

		# Behavior comments:



	def create(self):
		# x:732 y:426, x:722 y:239
		_state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])
		_state_machine.userdata.move_group = "manipulator"
		_state_machine.userdata.rotation = 0
		_state_machine.userdata.pick_configuration = []
		_state_machine.userdata.False_value = 0

		# Additional creation code can be added inside the following tags
		# [MANUAL_CREATE]
		
		# [/MANUAL_CREATE]


		with _state_machine:
			# x:8 y:64
			OperatableStateMachine.add('Retry Home',
										WaitState(wait_time=1),
										transitions={'done': 'Move home'},
										autonomy={'done': Autonomy.Off})

			# x:143 y:134
			OperatableStateMachine.add('DropAGV',
										SrdfStateToMoveit(config_name="DropPos", move_group="manipulator", action_topic='/move_group', robot_name=""),
										transitions={'reached': 'Gripper uit', 'planning_failed': 'failed', 'control_failed': 'Retry AGV', 'param_error': 'failed'},
										autonomy={'reached': Autonomy.Off, 'planning_failed': Autonomy.Off, 'control_failed': Autonomy.Off, 'param_error': Autonomy.Off},
										remapping={'config_name': 'config_name', 'move_group': 'move_group', 'robot_name': 'robot_name', 'action_topic': 'action_topic', 'joint_values': 'joint_values', 'joint_names': 'joint_names'})

			# x:140 y:402
			OperatableStateMachine.add('Return home',
										SrdfStateToMoveit(config_name="HomePos", move_group="manipulator", action_topic='/move_group', robot_name=""),
										transitions={'reached': 'finished', 'planning_failed': 'failed', 'control_failed': 'Retry Return', 'param_error': 'failed'},
										autonomy={'reached': Autonomy.Off, 'planning_failed': Autonomy.Off, 'control_failed': Autonomy.Off, 'param_error': Autonomy.Off},
										remapping={'config_name': 'config_name', 'move_group': 'move_group', 'robot_name': 'robot_name', 'action_topic': 'action_topic', 'joint_values': 'joint_values', 'joint_names': 'joint_names'})

			# x:8 y:126
			OperatableStateMachine.add('Retry AGV',
										WaitState(wait_time=1),
										transitions={'done': 'DropAGV'},
										autonomy={'done': Autonomy.Off})

			# x:0 y:393
			OperatableStateMachine.add('Retry Return',
										WaitState(wait_time=1),
										transitions={'done': 'Return home'},
										autonomy={'done': Autonomy.Off})

			# x:144 y:64
			OperatableStateMachine.add('Move home',
										SrdfStateToMoveit(config_name="HomePos", move_group="manipulator", action_topic='/move_group', robot_name=""),
										transitions={'reached': 'DropAGV', 'planning_failed': 'failed', 'control_failed': 'Retry Home', 'param_error': 'failed'},
										autonomy={'reached': Autonomy.Off, 'planning_failed': Autonomy.Off, 'control_failed': Autonomy.Off, 'param_error': Autonomy.Off},
										remapping={'config_name': 'config_name', 'move_group': 'move_group', 'robot_name': 'robot_name', 'action_topic': 'action_topic', 'joint_values': 'joint_values', 'joint_names': 'joint_names'})

			# x:150 y:218
			OperatableStateMachine.add('Gripper uit',
										PublisherBoolState(topic='/Gripper_Pomp'),
										transitions={'done': 'VacuumCheck'},
										autonomy={'done': Autonomy.Off},
										remapping={'value': 'False_value'})

			# x:157 y:294
			OperatableStateMachine.add('VacuumCheck',
										SubscriberState(topic='/Gripper_Vacuum', blocking=True, clear=False),
										transitions={'received': 'Return home', 'unavailable': 'failed'},
										autonomy={'received': Autonomy.Off, 'unavailable': Autonomy.Off},
										remapping={'message': 'message'})


		return _state_machine


	# Private functions can be added inside the following tags
	# [MANUAL_FUNC]
	
	# [/MANUAL_FUNC]
