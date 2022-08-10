#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################################
#               WARNING: Generated code!                  #
#              **************************                 #
# Manual changes may get lost if file is generated again. #
# Only code inside the [MANUAL] tags will be kept.        #
###########################################################

from flexbe_core import Behavior, Autonomy, OperatableStateMachine, ConcurrencyContainer, PriorityContainer, Logger
from hand_eye_flexbe_states.compute_calib import ComputeCalibState
from hand_eye_flexbe_states.execute_traj import TrajectoryExecuteState
from hand_eye_flexbe_states.find_charuco import FindCharucoState
from hand_eye_flexbe_states.get_calib_pose import GetCalibPoseState
from hand_eye_flexbe_states.move_charuco_center import MoveCharucoCenterState
from hand_eye_flexbe_states.pose_plan import PosePlanState
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]

# [/MANUAL_IMPORT]


'''
Created on Tue Nov 09 2021
@author: Andy Chien
'''
class HandEyeCalibrationSM(Behavior):
	'''
	Used to calibrate the camera on hand or in hand
	'''


	def __init__(self):
		super(HandEyeCalibrationSM, self).__init__()
		self.name = 'Hand Eye Calibration'

		# parameters of this behavior
		self.add_parameter('eye_in_hand', False)
		self.add_parameter('group_name', 'manipulator')

		# references to used behaviors

		# Additional initialization code can be added inside the following tags
		# [MANUAL_INIT]
		
		# [/MANUAL_INIT]

		# Behavior comments:



	def create(self):
		# x:421 y:521, x:130 y:365
		_state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])

		# Additional creation code can be added inside the following tags
		# [MANUAL_CREATE]
		
		# [/MANUAL_CREATE]


		with _state_machine:
			# x:47 y:115
			OperatableStateMachine.add('Find Charuco To Move',
										FindCharucoState(),
										transitions={'done': 'Move Charuco Center', 'fail': 'failed'},
										autonomy={'done': Autonomy.Off, 'fail': Autonomy.Off})

			# x:822 y:289
			OperatableStateMachine.add('Execute Traj',
										TrajectoryExecuteState(group_name=self.group_name),
										transitions={'done': 'Find Charuco', 'failed': 'failed', 'collision': 'Pose Plan'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off, 'collision': Autonomy.Off},
										remapping={'joint_trajectory': 'joint_trajectory', 'target_joints': 'target_joints', 'joint_config': 'joint_config'})

			# x:634 y:114
			OperatableStateMachine.add('Execute Traj To Center',
										TrajectoryExecuteState(group_name=self.group_name),
										transitions={'done': 'Get Calib Pose', 'failed': 'failed', 'collision': 'Pose Plan To Center'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off, 'collision': Autonomy.Off},
										remapping={'joint_trajectory': 'joint_trajectory', 'target_joints': 'target_joints', 'joint_config': 'joint_config'})

			# x:559 y:442
			OperatableStateMachine.add('Find Charuco',
										FindCharucoState(),
										transitions={'done': 'Get Calib Pose', 'fail': 'failed'},
										autonomy={'done': Autonomy.Off, 'fail': Autonomy.Off})

			# x:322 y:314
			OperatableStateMachine.add('Get Calib Pose',
										GetCalibPoseState(),
										transitions={'done': 'Pose Plan', 'fail': 'Calib Compute'},
										autonomy={'done': Autonomy.Off, 'fail': Autonomy.Off})

			# x:210 y:115
			OperatableStateMachine.add('Move Charuco Center',
										MoveCharucoCenterState(),
										transitions={'done': 'Pose Plan To Center', 'fail': 'failed'},
										autonomy={'done': Autonomy.Off, 'fail': Autonomy.Off})

			# x:571 y:261
			OperatableStateMachine.add('Pose Plan',
										PosePlanState(group_name=self.group_name),
										transitions={'failed': 'Get Calib Pose', 'done': 'Execute Traj'},
										autonomy={'failed': Autonomy.Off, 'done': Autonomy.Off},
										remapping={'joint_trajectory': 'joint_trajectory', 'target_joints': 'target_joints'})

			# x:404 y:119
			OperatableStateMachine.add('Pose Plan To Center',
										PosePlanState(group_name=self.group_name),
										transitions={'failed': 'failed', 'done': 'Execute Traj To Center'},
										autonomy={'failed': Autonomy.Off, 'done': Autonomy.Off},
										remapping={'joint_trajectory': 'joint_trajectory', 'target_joints': 'target_joints'})

			# x:320 y:445
			OperatableStateMachine.add('Calib Compute',
										ComputeCalibState(),
										transitions={'done': 'finished', 'fail': 'failed'},
										autonomy={'done': Autonomy.Off, 'fail': Autonomy.Off})


		return _state_machine


	# Private functions can be added inside the following tags
	# [MANUAL_FUNC]
	
	# [/MANUAL_FUNC]
