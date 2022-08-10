#!/usr/bin/env python
###########################################################
#               WARNING: Generated code!                  #
#              **************************                 #
# Manual changes may get lost if file is generated again. #
# Only code inside the [MANUAL] tags will be kept.        #
###########################################################

from flexbe_core import Behavior, Autonomy, OperatableStateMachine, ConcurrencyContainer, PriorityContainer, Logger
from flex_nav_flexbe_states.timed_stop_state import TimedStopState
from flex_nav_flexbe_states.clear_costmaps_state import ClearCostmapsState
from flexbe_states.log_state import LogState
from flex_nav_flexbe_states.move_distance_state import MoveDistanceState
from flexbe_states.operator_decision_state import OperatorDecisionState

# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]

# [/MANUAL_IMPORT]


'''
Created on Mon Jan 09 2017
@author: Justin Willis
'''
class TurtlebotSimpleRecoverySM(Behavior):
    '''
    Stops the robot, backs up, and clears the cost map.  Operator can bypass steps in lower autonomy levels.
    '''


    def __init__(self):
        super(TurtlebotSimpleRecoverySM, self).__init__()
        self.name = 'Turtlebot Simple Recovery'

        # parameters of this behavior

        # references to used behaviors

        # Additional initialization code can be added inside the following tags
        # [MANUAL_INIT]

		# [/MANUAL_INIT]

        # Behavior comments:



    def create(self):
        # x:869 y:327, x:226 y:285
        _state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])

        # Additional creation code can be added inside the following tags
        # [MANUAL_CREATE]

		# [/MANUAL_CREATE]


        with _state_machine:
            # x:70 y:38
            OperatableStateMachine.add('EStop',
                                        TimedStopState(timeout=0.25, cmd_topic='stamped_cmd_vel_mux/input/navi', odom_topic='mobile_base/odom'),
                                        transitions={'done': 'BackupQuery', 'failed': 'EStopFailure'},
                                        autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off})

            # x:810 y:144
            OperatableStateMachine.add('Clear Costmap',
                                        ClearCostmapsState(costmap_topics=['high_level_planner/clear_costmap','low_level_planner/clear_costmap'], timeout=5.0),
                                        transitions={'done': 'Cleared', 'failed': 'CostmapFailure'},
                                        autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off})

            # x:75 y:225
            OperatableStateMachine.add('EStopFailure',
                                        LogState(text="Emergency stop failure", severity=Logger.REPORT_ERROR),
                                        transitions={'done': 'failed'},
                                        autonomy={'done': Autonomy.Off})

            # x:309 y:213
            OperatableStateMachine.add('CostmapFailure',
                                        LogState(text="Failed to clear costmaps", severity=Logger.REPORT_WARN),
                                        transitions={'done': 'failed'},
                                        autonomy={'done': Autonomy.Off})

            # x:617 y:40
            OperatableStateMachine.add('ShortBackup',
                                        MoveDistanceState(target_time=2.0, distance=-0.175, cmd_topic='stamped_cmd_vel_mux/input/navi', odometry_topic='mobile_base/odom'),
                                        transitions={'done': 'ClearCostmapQuery', 'failed': 'ClearCostmapQuery'},
                                        autonomy={'done': Autonomy.Off, 'failed': Autonomy.Low})

            # x:447 y:257
            OperatableStateMachine.add('ClearCostmapQuery',
                                        OperatorDecisionState(outcomes=["yes","no"], hint="Do you wish to clear costmaps?", suggestion="no"),
                                        transitions={'yes': 'Clear Costmap', 'no': 'SkipClearCostmap'},
                                        autonomy={'yes': Autonomy.Full, 'no': Autonomy.High})

            # x:647 y:319
            OperatableStateMachine.add('SkipClearCostmap',
                                        LogState(text="Do not clear costmaps", severity=Logger.REPORT_INFO),
                                        transitions={'done': 'finished'},
                                        autonomy={'done': Autonomy.Off})

            # x:842 y:237
            OperatableStateMachine.add('Cleared',
                                        LogState(text="Cleared the costmaps", severity=Logger.REPORT_INFO),
                                        transitions={'done': 'finished'},
                                        autonomy={'done': Autonomy.Off})

            # x:257 y:40
            OperatableStateMachine.add('BackupQuery',
                                        OperatorDecisionState(outcomes=["long","short","no"], hint="Backup?", suggestion="short"),
                                        transitions={'no': 'ClearCostmapQuery', 'long': 'LongBackup', 'short': 'ShortBackup'},
                                        autonomy={'no': Autonomy.Full, 'long': Autonomy.Full, 'short': Autonomy.High})

            # x:459 y:81
            OperatableStateMachine.add('LongBackup',
                                        MoveDistanceState(target_time=4.0, distance=-0.35, cmd_topic='stamped_cmd_vel_mux/input/navi', odometry_topic='mobile_base/odom'),
                                        transitions={'done': 'ClearCostmapQuery', 'failed': 'ClearCostmapQuery'},
                                        autonomy={'done': Autonomy.Off, 'failed': Autonomy.Low})


        return _state_machine


    # Private functions can be added inside the following tags
    # [MANUAL_FUNC]

	# [/MANUAL_FUNC]
