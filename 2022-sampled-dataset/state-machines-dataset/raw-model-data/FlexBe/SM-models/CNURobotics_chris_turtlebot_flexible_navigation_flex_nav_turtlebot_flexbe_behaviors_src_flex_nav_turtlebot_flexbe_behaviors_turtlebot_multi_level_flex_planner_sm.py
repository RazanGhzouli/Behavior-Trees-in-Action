#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################################
#               WARNING: Generated code!                  #
#              **************************                 #
# Manual changes may get lost if file is generated again. #
# Only code inside the [MANUAL] tags will be kept.        #
###########################################################

from flexbe_core import Behavior, Autonomy, OperatableStateMachine, ConcurrencyContainer, PriorityContainer, Logger
from flex_nav_flexbe_states.clear_costmaps_state import ClearCostmapsState
from flex_nav_flexbe_states.get_path_state import GetPathState
from flexbe_states.operator_decision_state import OperatorDecisionState
from flex_nav_flexbe_states.follow_path_state import FollowPathState
from flex_nav_turtlebot_flexbe_states.turtlebot_status_state import TurtlebotStatusState
from flex_nav_flexbe_states.follow_topic_state import FollowTopicState
from flex_nav_turtlebot_flexbe_behaviors.turtlebot_simple_recovery_sm import TurtlebotSimpleRecoverySM
from flexbe_states.log_state import LogState
from flex_nav_flexbe_states.get_pose_state import GetPoseState
from flex_nav_flexbe_states.timed_stop_state import TimedStopState
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]

# [/MANUAL_IMPORT]


'''
Created on Thursday 13-June-2019
@author: David Conner
'''
class TurtlebotMultiLevelFlexPlannerSM(Behavior):
    '''
    Uses Flexible Navigation to control the Turtlebot robot with 3-level planning.
high-level: Map only 
mid-level: Smaller map area with sensors 
low-level: sensors only
    '''


    def __init__(self):
        super(TurtlebotMultiLevelFlexPlannerSM, self).__init__()
        self.name = 'Turtlebot Multi-Level Flex Planner'

        # parameters of this behavior

        # references to used behaviors
        self.add_behavior(TurtlebotSimpleRecoverySM, 'Turtlebot Simple Recovery')

        # Additional initialization code can be added inside the following tags
        # [MANUAL_INIT]

		# [/MANUAL_INIT]

        # Behavior comments:



    def create(self):
        # x:807 y:293, x:1163 y:18
        _state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])

        # Additional creation code can be added inside the following tags
        # [MANUAL_CREATE]

		# [/MANUAL_CREATE]

        # x:458 y:77, x:455 y:214, x:689 y:417, x:465 y:140, x:693 y:471, x:617 y:378, x:622 y:266, x:619 y:313, x:134 y:502, x:50 y:500, x:208 y:503, x:278 y:504
        _sm_container_0 = ConcurrencyContainer(outcomes=['finished', 'failed', 'danger', 'preempted'], input_keys=['plan'], conditions=[
                                        ('failed', [('MidLevel', 'failed')]),
                                        ('finished', [('MidLevel', 'done')]),
                                        ('preempted', [('MidLevel', 'preempted')]),
                                        ('danger', [('Safety', 'cliff')]),
                                        ('danger', [('Safety', 'bumper')]),
                                        ('finished', [('DWA2', 'done')]),
                                        ('failed', [('DWA2', 'failed')]),
                                        ('preempted', [('DWA2', 'preempted')])
                                        ])

        with _sm_container_0:
            # x:146 y:53
            OperatableStateMachine.add('MidLevel',
                                        FollowPathState(topic="mid_level_planner"),
                                        transitions={'done': 'finished', 'failed': 'failed', 'preempted': 'preempted'},
                                        autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off, 'preempted': Autonomy.Off},
                                        remapping={'plan': 'plan'})

            # x:401 y:420
            OperatableStateMachine.add('Safety',
                                        TurtlebotStatusState(bumper_topic='mobile_base/events/bumper', cliff_topic='mobile_base/events/cliff'),
                                        transitions={'bumper': 'danger', 'cliff': 'danger'},
                                        autonomy={'bumper': Autonomy.Off, 'cliff': Autonomy.Off})

            # x:274 y:257
            OperatableStateMachine.add('DWA2',
                                        FollowTopicState(planner_topic="mid_level_planner/SBPLLatticePlanner/plan", controller_topic="low_level_planner"),
                                        transitions={'done': 'finished', 'failed': 'failed', 'preempted': 'preempted'},
                                        autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off, 'preempted': Autonomy.Off})



        with _state_machine:
            # x:193 y:26
            OperatableStateMachine.add('ClearCostmap',
                                        ClearCostmapsState(costmap_topics=['high_level_planner/clear_costmap','low_level_planner/clear_costmap'], timeout=5.0),
                                        transitions={'done': 'Receive Goal', 'failed': 'failed'},
                                        autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off})

            # x:205 y:207
            OperatableStateMachine.add('Receive Path',
                                        GetPathState(planner_topic="high_level_planner"),
                                        transitions={'planned': 'ExecutePlan', 'empty': 'Continue', 'failed': 'Continue'},
                                        autonomy={'planned': Autonomy.Off, 'empty': Autonomy.Low, 'failed': Autonomy.Low},
                                        remapping={'goal': 'goal', 'plan': 'plan'})

            # x:218 y:342
            OperatableStateMachine.add('ExecutePlan',
                                        OperatorDecisionState(outcomes=["yes","no"], hint="Execute the current plan?", suggestion="yes"),
                                        transitions={'yes': 'Container', 'no': 'Continue'},
                                        autonomy={'yes': Autonomy.High, 'no': Autonomy.Full})

            # x:446 y:275
            OperatableStateMachine.add('Container',
                                        _sm_container_0,
                                        transitions={'finished': 'Log Success', 'failed': 'AutoReplan', 'danger': 'EStop', 'preempted': 'Continue'},
                                        autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit, 'danger': Autonomy.Inherit, 'preempted': Autonomy.Inherit},
                                        remapping={'plan': 'plan'})

            # x:435 y:146
            OperatableStateMachine.add('Continue',
                                        OperatorDecisionState(outcomes=["yes","no","recover","clearcostmap"], hint="Continue planning to new goal?", suggestion="yes"),
                                        transitions={'yes': 'Receive Goal', 'no': 'finished', 'recover': 'LogRecovery', 'clearcostmap': 'ClearCostmap'},
                                        autonomy={'yes': Autonomy.High, 'no': Autonomy.Full, 'recover': Autonomy.Full, 'clearcostmap': Autonomy.Full})

            # x:1052 y:227
            OperatableStateMachine.add('Turtlebot Simple Recovery',
                                        self.use_behavior(TurtlebotSimpleRecoverySM, 'Turtlebot Simple Recovery'),
                                        transitions={'finished': 'AutoReplan', 'failed': 'failed'},
                                        autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit})

            # x:664 y:307
            OperatableStateMachine.add('Log Success',
                                        LogState(text="Success!", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'Continue'},
                                        autonomy={'done': Autonomy.Off})

            # x:664 y:374
            OperatableStateMachine.add('Log Fail',
                                        LogState(text="Path execution failure", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'Recover'},
                                        autonomy={'done': Autonomy.Off})

            # x:960 y:70
            OperatableStateMachine.add('Log Recovered',
                                        LogState(text="Re-plan after recovery", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'New Plan'},
                                        autonomy={'done': Autonomy.Off})

            # x:772 y:71
            OperatableStateMachine.add('New Plan',
                                        GetPathState(planner_topic="high_level_planner"),
                                        transitions={'planned': 'Container', 'empty': 'Receive Goal', 'failed': 'Continue'},
                                        autonomy={'planned': Autonomy.Off, 'empty': Autonomy.Off, 'failed': Autonomy.Off},
                                        remapping={'goal': 'goal', 'plan': 'plan'})

            # x:203 y:113
            OperatableStateMachine.add('Receive Goal',
                                        GetPoseState(topic='flex_nav_global/goal'),
                                        transitions={'done': 'Receive Path'},
                                        autonomy={'done': Autonomy.Low},
                                        remapping={'goal': 'goal'})

            # x:866 y:374
            OperatableStateMachine.add('Recover',
                                        OperatorDecisionState(outcomes=["yes","no"], hint="Should we attempt recovery?", suggestion="yes"),
                                        transitions={'yes': 'LogRecovery', 'no': 'finished'},
                                        autonomy={'yes': Autonomy.High, 'no': Autonomy.Full})

            # x:887 y:236
            OperatableStateMachine.add('LogRecovery',
                                        LogState(text="Starting recovery behavior", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'Turtlebot Simple Recovery'},
                                        autonomy={'done': Autonomy.Off})

            # x:875 y:162
            OperatableStateMachine.add('AutoReplan',
                                        OperatorDecisionState(outcomes=["yes","no"], hint="Re-plan to current goal?", suggestion="yes"),
                                        transitions={'yes': 'Log Recovered', 'no': 'Continue'},
                                        autonomy={'yes': Autonomy.High, 'no': Autonomy.Full})

            # x:453 y:376
            OperatableStateMachine.add('EStop',
                                        TimedStopState(timeout=0.25, cmd_topic='stamped_cmd_vel_mux/input/navi', odom_topic='mobile_base/odom'),
                                        transitions={'done': 'Log Fail', 'failed': 'Log Fail'},
                                        autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off})


        return _state_machine


    # Private functions can be added inside the following tags
    # [MANUAL_FUNC]

	# [/MANUAL_FUNC]
