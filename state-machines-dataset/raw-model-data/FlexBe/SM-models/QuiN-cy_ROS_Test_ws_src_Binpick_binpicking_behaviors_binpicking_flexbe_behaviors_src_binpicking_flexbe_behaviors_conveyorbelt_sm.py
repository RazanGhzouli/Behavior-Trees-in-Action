#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################################
#               WARNING: Generated code!                  #
#              **************************                 #
# Manual changes may get lost if file is generated again. #
# Only code inside the [MANUAL] tags will be kept.        #
###########################################################

from flexbe_core import Behavior, Autonomy, OperatableStateMachine, ConcurrencyContainer, PriorityContainer, Logger
from flexbe_states.publisher_bool_state import PublisherBoolState
from flexbe_states.subscriber_state import SubscriberState
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]

# [/MANUAL_IMPORT]


'''
Created on Fri Jun 11 2021
@author: Quincy de Jong, Youp de Haas
'''
class ConveyorBeltSM(Behavior):
	'''
	Starting and stopping of the conveyorbelt
	'''


	def __init__(self):
		super(ConveyorBeltSM, self).__init__()
		self.name = 'ConveyorBelt'

		# parameters of this behavior

		# references to used behaviors

		# Additional initialization code can be added inside the following tags
		# [MANUAL_INIT]
		
		# [/MANUAL_INIT]

		# Behavior comments:



	def create(self):
		# x:152 y:534, x:424 y:147
		_state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])
		_state_machine.userdata.True_Value = 1
		_state_machine.userdata.False_Value = 0

		# Additional creation code can be added inside the following tags
		# [MANUAL_CREATE]
		
		# [/MANUAL_CREATE]


		with _state_machine:
			# x:99 y:36
			OperatableStateMachine.add('StartBand',
										PublisherBoolState(topic='/Band_Motor'),
										transitions={'done': 'CheckBandSensor'},
										autonomy={'done': Autonomy.Off},
										remapping={'value': 'True_Value'})

			# x:94 y:120
			OperatableStateMachine.add('CheckBandSensor',
										SubscriberState(topic='/Band_Sensor_End', blocking=True, clear=True),
										transitions={'received': 'StartBand_2', 'unavailable': 'failed'},
										autonomy={'received': Autonomy.Off, 'unavailable': Autonomy.Off},
										remapping={'message': 'message'})

			# x:104 y:308
			OperatableStateMachine.add('StartBand_2',
										PublisherBoolState(topic='/Band_Motor'),
										transitions={'done': 'finished'},
										autonomy={'done': Autonomy.Off},
										remapping={'value': 'False_Value'})


		return _state_machine


	# Private functions can be added inside the following tags
	# [MANUAL_FUNC]
	
	# [/MANUAL_FUNC]
