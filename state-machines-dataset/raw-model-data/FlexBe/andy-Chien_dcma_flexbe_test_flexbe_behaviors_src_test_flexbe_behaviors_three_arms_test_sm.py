#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################################
#               WARNING: Generated code!                  #
#              **************************                 #
# Manual changes may get lost if file is generated again. #
# Only code inside the [MANUAL] tags will be kept.        #
###########################################################

from flexbe_core import Behavior, Autonomy, OperatableStateMachine, ConcurrencyContainer, PriorityContainer, Logger
from test_flexbe_behaviors.test_behaviors_sm import TestBehaviorsSM
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]

# [/MANUAL_IMPORT]


'''
Created on Thu Jul 08 2021
@author: Andy Chien
'''
class ThreeArmsTestSM(Behavior):
	'''
	test three arms with dcma planner in one time
	'''


	def __init__(self):
		super(ThreeArmsTestSM, self).__init__()
		self.name = 'Three Arms Test'

		# parameters of this behavior

		# references to used behaviors
		self.add_behavior(TestBehaviorsSM, 'Container/Test Behaviors')
		self.add_behavior(TestBehaviorsSM, 'Container/Test Behaviors 2')
		self.add_behavior(TestBehaviorsSM, 'Container/Test Behaviors 3')

		# Additional initialization code can be added inside the following tags
		# [MANUAL_INIT]
		
		# [/MANUAL_INIT]

		# Behavior comments:



	def create(self):
		# x:30 y:365, x:130 y:365
		_state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])

		# Additional creation code can be added inside the following tags
		# [MANUAL_CREATE]
		
		# [/MANUAL_CREATE]

		# x:30 y:463, x:130 y:463, x:230 y:463, x:330 y:463
		_sm_container_0 = ConcurrencyContainer(outcomes=['finished', 'failed'], conditions=[
										('finished', [('Test Behaviors', 'finished'), ('Test Behaviors 2', 'finished'), ('Test Behaviors 3', 'finished')]),
										('failed', [('Test Behaviors', 'failed'), ('Test Behaviors 2', 'failed'), ('Test Behaviors 3', 'failed')])
										])

		with _sm_container_0:
			# x:83 y:103
			OperatableStateMachine.add('Test Behaviors',
										self.use_behavior(TestBehaviorsSM, 'Container/Test Behaviors',
											parameters={'planner_topic': "robot_0/dcma_planner/move_group", 'robot_topic': "robot_0/arm_controller/follow_joint_trajectory", 'robot_id': 0}),
										transitions={'finished': 'finished', 'failed': 'failed'},
										autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit})

			# x:332 y:104
			OperatableStateMachine.add('Test Behaviors 2',
										self.use_behavior(TestBehaviorsSM, 'Container/Test Behaviors 2',
											parameters={'planner_topic': "robot_1/dcma_planner/move_group", 'robot_topic': "robot_1/arm_controller/follow_joint_trajectory", 'robot_id': 1}),
										transitions={'finished': 'finished', 'failed': 'failed'},
										autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit})

			# x:588 y:107
			OperatableStateMachine.add('Test Behaviors 3',
										self.use_behavior(TestBehaviorsSM, 'Container/Test Behaviors 3',
											parameters={'planner_topic': "robot_2/dcma_planner/move_group", 'robot_topic': "robot_2/arm_controller/follow_joint_trajectory", 'robot_id': 2}),
										transitions={'finished': 'finished', 'failed': 'failed'},
										autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit})



		with _state_machine:
			# x:138 y:86
			OperatableStateMachine.add('Container',
										_sm_container_0,
										transitions={'finished': 'finished', 'failed': 'failed'},
										autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit})


		return _state_machine


	# Private functions can be added inside the following tags
	# [MANUAL_FUNC]
	
	# [/MANUAL_FUNC]
