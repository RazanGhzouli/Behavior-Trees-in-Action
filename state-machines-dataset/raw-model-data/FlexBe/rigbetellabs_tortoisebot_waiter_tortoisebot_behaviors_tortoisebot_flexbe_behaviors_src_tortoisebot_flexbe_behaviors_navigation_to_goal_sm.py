#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################################
#               WARNING: Generated code!                  #
#              **************************                 #
# Manual changes may get lost if file is generated again. #
# Only code inside the [MANUAL] tags will be kept.        #
###########################################################

from flexbe_core import Behavior, Autonomy, OperatableStateMachine, ConcurrencyContainer, PriorityContainer, Logger
from tortoisebot_flexbe_states.move_base_state import MoveBaseState
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]
from geometry_msgs.msg import Pose2D
# [/MANUAL_IMPORT]


'''
Created on Sun May 30 2021
@author: Shubham Takbhate
'''
class Navigation_to_goalSM(Behavior):
	'''
	Use the behavior for going to a particualr goal
	'''


	def __init__(self):
		super(Navigation_to_goalSM, self).__init__()
		self.name = 'Navigation_to_goal'

		# parameters of this behavior

		# references to used behaviors

		# Additional initialization code can be added inside the following tags
		# [MANUAL_INIT]
		
		# [/MANUAL_INIT]

		# Behavior comments:



	def create(self):
		table_1 = Pose2D(x=-0.4, y=0.3, theta=1)
		table_2 = Pose2D(x=-0.3, y=-0.3, theta=1)
		Counter = Pose2D(x=0, y=0, theta=1)
		# x:30 y:275, x:130 y:275
		_state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])
		_state_machine.userdata.table_1 = table_1
		_state_machine.userdata.table_2 = table_2
		_state_machine.userdata.Counter = Counter

		# Additional creation code can be added inside the following tags
		# [MANUAL_CREATE]
		
		# [/MANUAL_CREATE]


		with _state_machine:
			# x:30 y:40
			OperatableStateMachine.add('Navtogoal',
										MoveBaseState(),
										transitions={'arrived': 'Return to counter', 'failed': 'failed'},
										autonomy={'arrived': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'waypoint': 'table_1'})

			# x:260 y:159
			OperatableStateMachine.add('Return to counter',
										MoveBaseState(),
										transitions={'arrived': 'finished', 'failed': 'failed'},
										autonomy={'arrived': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'waypoint': 'Counter'})


		return _state_machine


	# Private functions can be added inside the following tags
	# [MANUAL_FUNC]
	
	# [/MANUAL_FUNC]
