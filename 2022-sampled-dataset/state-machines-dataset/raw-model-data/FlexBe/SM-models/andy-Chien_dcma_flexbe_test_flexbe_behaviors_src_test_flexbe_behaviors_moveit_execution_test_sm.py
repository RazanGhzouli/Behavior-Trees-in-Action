#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################################
#               WARNING: Generated code!                  #
#              **************************                 #
# Manual changes may get lost if file is generated again. #
# Only code inside the [MANUAL] tags will be kept.        #
###########################################################

from flexbe_core import Behavior, Autonomy, OperatableStateMachine, ConcurrencyContainer, PriorityContainer, Logger
from test_flexbe_states.execute_traj import TrajectoryExecuteState
from test_flexbe_states.get_joints_symple import GetJointSymple
from test_flexbe_states.joints_plan import JointsPlan
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]

# [/MANUAL_IMPORT]


'''
Created on Mon Nov 01 2021
@author: Andy Chien
'''
class MoveitExecutionTestSM(Behavior):
	'''
	test moveit execution capability
	'''


	def __init__(self):
		super(MoveitExecutionTestSM, self).__init__()
		self.name = 'Moveit Execution Test'

		# parameters of this behavior
		self.add_parameter('group_name', 'manipulator')

		# references to used behaviors

		# Additional initialization code can be added inside the following tags
		# [MANUAL_INIT]
		
		# [/MANUAL_INIT]

		# Behavior comments:



	def create(self):
		# x:30 y:345, x:295 y:137
		_state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])

		# Additional creation code can be added inside the following tags
		# [MANUAL_CREATE]
		
		# [/MANUAL_CREATE]


		with _state_machine:
			# x:90 y:181
			OperatableStateMachine.add('Get_Joints',
										GetJointSymple(),
										transitions={'done': 'Plan', 'finish': 'finished'},
										autonomy={'done': Autonomy.Off, 'finish': Autonomy.Off},
										remapping={'joint_config': 'joint_config'})

			# x:248 y:24
			OperatableStateMachine.add('Plan',
										JointsPlan(group_name=self.group_name),
										transitions={'failed': 'Plan', 'done': 'Execute_Trajectory'},
										autonomy={'failed': Autonomy.Off, 'done': Autonomy.Off},
										remapping={'joint_config': 'joint_config', 'joint_trajectory': 'joint_trajectory', 'target_joints': 'target_joints'})

			# x:506 y:198
			OperatableStateMachine.add('Execute_Trajectory',
										TrajectoryExecuteState(group_name=self.group_name),
										transitions={'done': 'Get_Joints', 'failed': 'failed', 'collision': 'Plan'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off, 'collision': Autonomy.Off},
										remapping={'joint_trajectory': 'joint_trajectory', 'target_joints': 'target_joints', 'joint_config': 'joint_config'})


		return _state_machine


	# Private functions can be added inside the following tags
	# [MANUAL_FUNC]
	
	# [/MANUAL_FUNC]
