#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################################
#               WARNING: Generated code!                  #
#              **************************                 #
# Manual changes may get lost if file is generated again. #
# Only code inside the [MANUAL] tags will be kept.        #
###########################################################

from flexbe_core import Behavior, Autonomy, OperatableStateMachine, ConcurrencyContainer, PriorityContainer, Logger
from binpicking_flexbe_behaviors.conveyorbelt_sm import ConveyorBeltSM
from binpicking_flexbe_behaviors.agv_place_sm import AGVPlaceSM
from binpicking_flexbe_behaviors.conveyor_pickup_sm import Conveyor_pickupSM
from flexbe_states.operator_decision_state import OperatorDecisionState
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]

# [/MANUAL_IMPORT]


'''
Created on Fri Jun 04 2021
@author: q / y
'''
class ProjectHelloRealworldROS1SM(Behavior):
	'''
	main project
	'''


	def __init__(self):
		super(ProjectHelloRealworldROS1SM, self).__init__()
		self.name = 'Project Hello Realworld ROS 1 '

		# parameters of this behavior

		# references to used behaviors
		self.add_behavior(ConveyorBeltSM, 'ConveyorBelt')
		self.add_behavior(AGVPlaceSM, 'AGV Place')
		self.add_behavior(Conveyor_pickupSM, 'Conveyor_pickup')

		# Additional initialization code can be added inside the following tags
		# [MANUAL_INIT]
		
		# [/MANUAL_INIT]

		# Behavior comments:



	def create(self):
		# x:1164 y:83, x:286 y:519
		_state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])

		# Additional creation code can be added inside the following tags
		# [MANUAL_CREATE]
		
		# [/MANUAL_CREATE]


		with _state_machine:
			# x:42 y:58
			OperatableStateMachine.add('ConveyorBelt',
										self.use_behavior(ConveyorBeltSM, 'ConveyorBelt'),
										transitions={'finished': 'Conveyor_pickup', 'failed': 'failed'},
										autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit})

			# x:514 y:91
			OperatableStateMachine.add('AGV Place',
										self.use_behavior(AGVPlaceSM, 'AGV Place'),
										transitions={'finished': 'opnieuw?', 'failed': 'failed'},
										autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit})

			# x:282 y:91
			OperatableStateMachine.add('Conveyor_pickup',
										self.use_behavior(Conveyor_pickupSM, 'Conveyor_pickup'),
										transitions={'finished': 'AGV Place', 'failed': 'failed'},
										autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit})

			# x:749 y:54
			OperatableStateMachine.add('opnieuw?',
										OperatorDecisionState(outcomes=['yes','no'], hint=None, suggestion=None),
										transitions={'yes': 'ConveyorBelt', 'no': 'finished'},
										autonomy={'yes': Autonomy.Off, 'no': Autonomy.Off})


		return _state_machine


	# Private functions can be added inside the following tags
	# [MANUAL_FUNC]
	
	# [/MANUAL_FUNC]
