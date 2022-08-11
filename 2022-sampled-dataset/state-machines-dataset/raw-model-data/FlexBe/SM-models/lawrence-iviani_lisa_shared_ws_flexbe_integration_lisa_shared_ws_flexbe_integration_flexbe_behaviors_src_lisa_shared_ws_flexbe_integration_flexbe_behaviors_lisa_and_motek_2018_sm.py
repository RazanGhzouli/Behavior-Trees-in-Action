#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################################
#               WARNING: Generated code!                  #
#              **************************                 #
# Manual changes may get lost if file is generated again. #
# Only code inside the [MANUAL] tags will be kept.        #
###########################################################

from flexbe_core import Behavior, Autonomy, OperatableStateMachine, ConcurrencyContainer, PriorityContainer, Logger
from flexbe_states.calculation_state import CalculationState
from flexbe_states.check_condition_state import CheckConditionState
from flexbe_states.log_key_state import LogKeyState
from flexbe_states.log_state import LogState
from flexbe_states.wait_state import WaitState
from horse_flexbe_states.part_available_pose_service_state import PartAvailablePoseService
from horse_flexbe_states.set_screw_service_state import SetScrewServiceState
from horse_flexbe_states.shared_ws_action_state import SharedWsActionState
from horse_flexbe_states.shared_ws_new_traj_action_state import SharedWsNewTrajActionState
from lisa_flexbe_states_flexbe_states.lisa_utter_actionlib_state import LisaUtterActionState
from lisa_flexbe_states_flexbe_states.lisa_utter_actionlib_state_with_uk import LisaUtterActionStateWithUserkey
from lisa_flexbe_states_flexbe_states.lisa_utter_and_wait_for_intent_state import LisaUtterAndWaitForIntentState
from lisa_shared_ws_flexbe_integration_flexbe_behaviors.gripper_complete_sm import GripperCompleteSM
from lisa_shared_ws_flexbe_integration_flexbe_states.check_is_gripper_finished import CheckGripperIsFinished
from lisa_shared_ws_flexbe_integration_flexbe_states.create_screw_string import LisaMotekConcatenateScrewPartString
from lisa_shared_ws_flexbe_integration_flexbe_states.get_gripper_screws_state import GripperStateListener
from lisa_shared_ws_flexbe_integration_flexbe_states.reset_screws_state_gripper import ResetScrewStatesInGripper
from shared_workspace_behaviors.motekinsertscrew_sm import MotekInsertScrewSM
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]

# [/MANUAL_IMPORT]


'''
Created on Nov 20 2020
@author: Lawrence Iviani
'''
class LisaandMotek2018SM(Behavior):
    '''
    Added acoustic communication channel, based on Motek 2018 with localization of parts and online trajectory computation
    '''


    def __init__(self):
        super(LisaandMotek2018SM, self).__init__()
        self.name = 'Lisa and Motek 2018'

        # parameters of this behavior

        # references to used behaviors
        self.add_behavior(GripperCompleteSM, 'Gripper Ended Check/Ask End Gripper status/Ask for Gripper Complete')
        self.add_behavior(MotekInsertScrewSM, 'MotekInsertScrew')

        # semantic properties of this behavior
        self._semantic_properties = {}

        # Additional initialization code can be added inside the following tags
        # [MANUAL_INIT]

        # [/MANUAL_INIT]

        # Behavior comments:

        # ! 330 253 /Grip Ended Check
        # TODO: add confirmation step here to add or not the screw to the list of done|n

        # ! 658 244 /Grip Ended Check/Group
        # There is a bug that doesnt wait the utterance (except the first time it is executed). This is a workaround

        # ! 0 186 /Grip Ended Check
        # There is a buggy condition (apparently), where the screw can be inserted but not found. The SM motek insert seems ok but the value for found doesnt change (is this a flexbe bug??)

        # O 1468 527 /Grip Ended Check
        # connect succeded from available screw in current gripper for an utterance

        # O 758 340 
        # debug only

        # O 17 319 /Grip Ended Check/Utter Wrong Insertion
        # for a reason i cant understand the wait time doesnt work here, i use a wait as fix and set to 0 in the uttering block

        # O 740 493 /Grip Ended Check
        # if false i need to reset the gripper

        # O 733 148 /Gripper Ended Check/Ask Once for retry
        # log and wait are for debug only



    def create(self):
        exec_speed = 0.80 #was scary at 0.35
        exec_acceleration = 1.00 # was scary at 0.40
        coll_threshold = 10 # was 14 with CVL at first, then 12 before switch to D435
        coll_repeats = 0
        utter_incomplete = 'The gripper is not finished'
        utter_complete = 'The gripper is finished, remove from the workspace'
        utter_next_screw = 'move, in the same gripper'
        utter_unknown = "Gripper is in an unknwon state"
        # x:1105 y:39, x:24 y:178
        _state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])
        _state_machine.userdata.eSELECT_AVAILABLE_TRAJ = 12
        _state_machine.userdata.eEXECUTE_FW = 1
        _state_machine.userdata.eREAD_FROM_DISK = 6
        _state_machine.userdata.eEXECUTE_BW = 2
        _state_machine.userdata.ZERO = 0
        _state_machine.userdata.endeffector_frame = 'tool_screwdriver_tip_link'
        _state_machine.userdata.reference_frame = 'base_link'
        _state_machine.userdata.tf_frame = 'screw_'
        _state_machine.userdata.velocity = 1.0
        _state_machine.userdata.target_offset = []
        _state_machine.userdata.offset_position_to_screw = [0.0 , 0.0, 0.003]
        _state_machine.userdata.offset_position_from_screw = [0.0 , 0.0, -0.022]
        _state_machine.userdata.offset_orientation_jiggle = [0.0, 0.0, 0.2, 1.0]
        _state_machine.userdata.no_offset_position = [0.0, 0.0, 0,0]
        _state_machine.userdata.no_offset_orientation = [0.0, 0.0, 0.0, 1.0]
        _state_machine.userdata.eDRIVE_TO_START = 11
        _state_machine.userdata.start_step = 0
        _state_machine.userdata.eSELECT_AVAILABLE_REPLAN_TRAJ = 14
        _state_machine.userdata.eEXECUTE_REPLAN_TRAJ = 15
        _state_machine.userdata.eEXECUTE_BW_FROM_STEP = 17
        _state_machine.userdata.eEXECUTE_FW_FROM_STEP = 16
        _state_machine.userdata.eCREATE_NEW_TRAJ = 19
        _state_machine.userdata.eEXECUTE_NEW_TRAJ = 20
        _state_machine.userdata.next_trajectory = 0
        _state_machine.userdata.list_available_screw_poses = []
        _state_machine.userdata.use_same_gripper = False
        _state_machine.userdata.same_gripper_retry = 0
        _state_machine.userdata.obstacle_traj_counter = 0
        _state_machine.userdata.interact_screw_failed = ""

        # Additional creation code can be added inside the following tags
        # [MANUAL_CREATE]

        # [/MANUAL_CREATE]

        # x:30 y:538, x:653 y:394
        _sm_utter_traj_aborted_0 = OperatableStateMachine(outcomes=['error', 'done'], input_keys=['obstacle_traj_counter'], output_keys=['obstacle_traj_counter'])

        with _sm_utter_traj_aborted_0:
            # x:397 y:39
            OperatableStateMachine.add('check_utter',
                                        CheckConditionState(predicate=lambda x: x > 0),
                                        transitions={'true': 'decrease_counter', 'false': 'reset_counter'},
                                        autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                        remapping={'input_value': 'obstacle_traj_counter'})

            # x:655 y:33
            OperatableStateMachine.add('decrease_counter',
                                        CalculationState(calculation=lambda x: x-1),
                                        transitions={'done': 'done'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'input_value': 'obstacle_traj_counter', 'output_value': 'obstacle_traj_counter'})

            # x:399 y:146
            OperatableStateMachine.add('reset_counter',
                                        CalculationState(calculation=lambda x: 10),
                                        transitions={'done': 'utter new traj aborted'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'input_value': 'obstacle_traj_counter', 'output_value': 'obstacle_traj_counter'})

            # x:377 y:261
            OperatableStateMachine.add('utter new traj aborted',
                                        LisaUtterActionState(text_to_utter="Trajectory execution was  aborted", wait_time=0),
                                        transitions={'uttered_all': 'done', 'timeout': 'done', 'command_error': 'error'},
                                        autonomy={'uttered_all': Autonomy.Off, 'timeout': Autonomy.Off, 'command_error': Autonomy.Off},
                                        remapping={'error_reason': 'error_reason'})


        # x:330 y:538, x:852 y:387
        _sm_utter_obstacle_1 = OperatableStateMachine(outcomes=['done', 'error'], input_keys=['obstacle_traj_counter'], output_keys=['obstacle_traj_counter'])

        with _sm_utter_obstacle_1:
            # x:97 y:62
            OperatableStateMachine.add('log_utt_obst',
                                        LogKeyState(text="obstacle_traj_counter is now: {}", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'check_utter_collision'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'data': 'obstacle_traj_counter'})

            # x:326 y:170
            OperatableStateMachine.add('decrease_utter_obstacle_counter',
                                        CalculationState(calculation=lambda x: x-1),
                                        transitions={'done': 'wait_debug'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'input_value': 'obstacle_traj_counter', 'output_value': 'obstacle_traj_counter'})

            # x:831 y:41
            OperatableStateMachine.add('reset_utter_collision_counter',
                                        CalculationState(calculation=lambda x: 10),
                                        transitions={'done': 'utter obstacle'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'input_value': 'obstacle_traj_counter', 'output_value': 'obstacle_traj_counter'})

            # x:785 y:188
            OperatableStateMachine.add('utter obstacle',
                                        LisaUtterActionState(text_to_utter="Avaialble screws,  but  there is an  obstacle", wait_time=0),
                                        transitions={'uttered_all': 'wait_debug', 'timeout': 'wait_debug', 'command_error': 'error'},
                                        autonomy={'uttered_all': Autonomy.Off, 'timeout': Autonomy.Off, 'command_error': Autonomy.Off},
                                        remapping={'error_reason': 'error_reason'})

            # x:284 y:342
            OperatableStateMachine.add('wait_debug',
                                        WaitState(wait_time=0.1),
                                        transitions={'done': 'done'},
                                        autonomy={'done': Autonomy.Off})

            # x:269 y:54
            OperatableStateMachine.add('check_utter_collision',
                                        CheckConditionState(predicate=lambda x: x > 0),
                                        transitions={'true': 'decrease_utter_obstacle_counter', 'false': 'reset_utter_collision_counter'},
                                        autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                        remapping={'input_value': 'obstacle_traj_counter'})


        # x:30 y:538, x:278 y:531
        _sm_check_same_gripper_2 = OperatableStateMachine(outcomes=['done', 'error'], input_keys=['same_gripper_retry', 'use_same_gripper'], output_keys=['use_same_gripper', 'same_gripper_retry'])

        with _sm_check_same_gripper_2:
            # x:30 y:40
            OperatableStateMachine.add('decrese_retry_same_gripper',
                                        CalculationState(calculation=lambda x: x-1),
                                        transitions={'done': 'Check_retry'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'input_value': 'same_gripper_retry', 'output_value': 'same_gripper_retry'})

            # x:569 y:150
            OperatableStateMachine.add('reset_another_gripper',
                                        CalculationState(calculation=lambda x: 3),
                                        transitions={'done': 'utter_change gripper'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'input_value': 'use_same_gripper', 'output_value': 'use_same_gripper'})

            # x:340 y:154
            OperatableStateMachine.add('set_another_gripper',
                                        CalculationState(calculation=lambda x: False),
                                        transitions={'done': 'reset_another_gripper'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'input_value': 'use_same_gripper', 'output_value': 'use_same_gripper'})

            # x:376 y:297
            OperatableStateMachine.add('utter_change gripper',
                                        LisaUtterActionState(text_to_utter="Change to another gripper", wait_time=0),
                                        transitions={'uttered_all': 'wait_debug', 'timeout': 'wait_debug', 'command_error': 'error'},
                                        autonomy={'uttered_all': Autonomy.Off, 'timeout': Autonomy.Off, 'command_error': Autonomy.Off},
                                        remapping={'error_reason': 'error_reason'})

            # x:83 y:387
            OperatableStateMachine.add('wait_debug',
                                        WaitState(wait_time=0.1),
                                        transitions={'done': 'done'},
                                        autonomy={'done': Autonomy.Off})

            # x:70 y:139
            OperatableStateMachine.add('Check_retry',
                                        CheckConditionState(predicate=lambda x: x> 0),
                                        transitions={'true': 'wait_debug', 'false': 'set_another_gripper'},
                                        autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                        remapping={'input_value': 'same_gripper_retry'})


        # x:664 y:503, x:1016 y:430
        _sm_search_and_move_to_next_screw_3 = OperatableStateMachine(outcomes=['error', 'moved_to_next_screw'], input_keys=['eEXECUTE_NEW_TRAJ', 'eCREATE_NEW_TRAJ', 'next_trajectory', 'list_available_screw_poses', 'use_same_gripper', 'same_gripper_retry', 'obstacle_traj_counter'], output_keys=['next_trajectory'])

        with _sm_search_and_move_to_next_screw_3:
            # x:92 y:22
            OperatableStateMachine.add('use_same_gripper',
                                        CheckConditionState(predicate=lambda x: x==True),
                                        transitions={'true': 'log_use_same_grip', 'false': 'log_use_another_grip'},
                                        autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                        remapping={'input_value': 'use_same_gripper'})

            # x:44 y:196
            OperatableStateMachine.add('Available Screws Same Gripper',
                                        PartAvailablePoseService(check_only_current_gripper=True),
                                        transitions={'succeeded': 'Find Collision Free Trajectory', 'aborted': 'Check same gripper'},
                                        autonomy={'succeeded': Autonomy.Off, 'aborted': Autonomy.Off},
                                        remapping={'last_trajectory_id': 'next_trajectory', 'list_available_parts': 'list_available_screw_poses'})

            # x:98 y:378
            OperatableStateMachine.add('Check same gripper',
                                        _sm_check_same_gripper_2,
                                        transitions={'done': 'WaitForScrews', 'error': 'error'},
                                        autonomy={'done': Autonomy.Inherit, 'error': Autonomy.Inherit},
                                        remapping={'same_gripper_retry': 'same_gripper_retry', 'use_same_gripper': 'use_same_gripper'})

            # x:958 y:253
            OperatableStateMachine.add('Execute New Trajectory',
                                        SharedWsActionState(exec_speed=exec_speed, exec_acceleration=exec_acceleration, coll_threshold=coll_threshold, coll_repeats=coll_repeats),
                                        transitions={'succeeded': 'set_retry', 'preempted': 'error', 'aborted': 'Utter traj aborted'},
                                        autonomy={'succeeded': Autonomy.Off, 'preempted': Autonomy.Off, 'aborted': Autonomy.Off},
                                        remapping={'action_id': 'eEXECUTE_NEW_TRAJ', 'trajectory_id': 'next_trajectory', 'results': 'results'})

            # x:597 y:178
            OperatableStateMachine.add('Find Collision Free Trajectory',
                                        SharedWsNewTrajActionState(exec_speed=exec_speed, exec_acceleration=exec_acceleration, coll_threshold=coll_threshold, coll_repeats=coll_repeats),
                                        transitions={'succeeded': 'Log_next_traj_id', 'preempted': 'error', 'aborted': 'wait_debug'},
                                        autonomy={'succeeded': Autonomy.Off, 'preempted': Autonomy.Off, 'aborted': Autonomy.Off},
                                        remapping={'action_id': 'eCREATE_NEW_TRAJ', 'trajectory_id': 'next_trajectory', 'list_available_screw_poses': 'list_available_screw_poses', 'results': 'results', 'next_trajectory': 'next_trajectory'})

            # x:979 y:136
            OperatableStateMachine.add('Log_next_traj_id',
                                        LogKeyState(text="MAIN: Next Free Tjact. ID is for screw : {}", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'Execute New Trajectory'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'data': 'next_trajectory'})

            # x:1132 y:26
            OperatableStateMachine.add('Sleep Until Retry',
                                        WaitState(wait_time=2),
                                        transitions={'done': 'use_same_gripper'},
                                        autonomy={'done': Autonomy.Off})

            # x:466 y:334
            OperatableStateMachine.add('Utter Obstacle',
                                        _sm_utter_obstacle_1,
                                        transitions={'done': 'WaitForScrews', 'error': 'error'},
                                        autonomy={'done': Autonomy.Inherit, 'error': Autonomy.Inherit},
                                        remapping={'obstacle_traj_counter': 'obstacle_traj_counter'})

            # x:1231 y:480
            OperatableStateMachine.add('Utter traj aborted',
                                        _sm_utter_traj_aborted_0,
                                        transitions={'error': 'error', 'done': 'Sleep Until Retry'},
                                        autonomy={'error': Autonomy.Inherit, 'done': Autonomy.Inherit},
                                        remapping={'obstacle_traj_counter': 'obstacle_traj_counter'})

            # x:291 y:258
            OperatableStateMachine.add('WaitForScrews',
                                        WaitState(wait_time=0.5),
                                        transitions={'done': 'use_same_gripper'},
                                        autonomy={'done': Autonomy.Off})

            # x:339 y:50
            OperatableStateMachine.add('log_use_another_grip',
                                        LogState(text="SMNS: use another gripper", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'Available Screws Request'},
                                        autonomy={'done': Autonomy.Off})

            # x:54 y:117
            OperatableStateMachine.add('log_use_same_grip',
                                        LogState(text="SMNS: use same gripper", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'Available Screws Same Gripper'},
                                        autonomy={'done': Autonomy.Off})

            # x:971 y:331
            OperatableStateMachine.add('set_retry',
                                        CalculationState(calculation=lambda x: 3),
                                        transitions={'done': 'moved_to_next_screw'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'input_value': 'same_gripper_retry', 'output_value': 'same_gripper_retry'})

            # x:521 y:254
            OperatableStateMachine.add('wait_debug',
                                        WaitState(wait_time=0.1),
                                        transitions={'done': 'Utter Obstacle'},
                                        autonomy={'done': Autonomy.Off})

            # x:628 y:51
            OperatableStateMachine.add('Available Screws Request',
                                        PartAvailablePoseService(check_only_current_gripper=False),
                                        transitions={'succeeded': 'Find Collision Free Trajectory', 'aborted': 'WaitForScrews'},
                                        autonomy={'succeeded': Autonomy.Off, 'aborted': Autonomy.Off},
                                        remapping={'last_trajectory_id': 'next_trajectory', 'list_available_parts': 'list_available_screw_poses'})


        # x:1070 y:391, x:497 y:422, x:895 y:410, x:1439 y:361, x:725 y:434
        _sm_update_screw_4 = OperatableStateMachine(outcomes=['operator_check', 'error', 'gripper_terminated', 'screws_available_same_gripper', 'missing_screws'], input_keys=['use_same_gripper', 'next_trajectory', 'insertion_successful', 'screw_found'], output_keys=['list_gripper_screws_status', 'list_available_screw_poses', 'use_same_gripper'])

        with _sm_update_screw_4:
            # x:33 y:33
            OperatableStateMachine.add('Update Screw State',
                                        SetScrewServiceState(),
                                        transitions={'succeeded': 'wait_screw_update', 'aborted': 'log_err_screws'},
                                        autonomy={'succeeded': Autonomy.Off, 'aborted': Autonomy.Off},
                                        remapping={'screw_id': 'next_trajectory', 'finished_successful': 'insertion_successful', 'screw_found': 'screw_found', 'result': 'error_reason'})

            # x:688 y:127
            OperatableStateMachine.add('debug_wait_1',
                                        WaitState(wait_time=0.3),
                                        transitions={'done': 'is_gripper_terminated'},
                                        autonomy={'done': Autonomy.Off})

            # x:395 y:93
            OperatableStateMachine.add('get_screw_in_gripper',
                                        GripperStateListener(input_id_is_screw=True, time_out=1.0, number_part_screws=4),
                                        transitions={'succeeded': 'debug_wait_1', 'aborted': 'log_err_screws'},
                                        autonomy={'succeeded': Autonomy.Off, 'aborted': Autonomy.Off},
                                        remapping={'selected_gripper_id': 'next_trajectory', 'gripper_status': 'gripper_status', 'list_gripper_screws_status': 'list_gripper_screws_status', 'gripper_id': 'gripper_id', 'gripper_name': 'gripper_name', 'error_reason': 'error_reason'})

            # x:805 y:161
            OperatableStateMachine.add('is_gripper_terminated',
                                        CheckGripperIsFinished(number_part_screws=4),
                                        transitions={'done': 'set_use_another_gripper', 'screws_available': 'set_use_same_gripper', 'operator_check': 'operator_check', 'error': 'error', 'missing_screws': 'missing_screws'},
                                        autonomy={'done': Autonomy.Off, 'screws_available': Autonomy.Off, 'operator_check': Autonomy.Off, 'error': Autonomy.Off, 'missing_screws': Autonomy.Off},
                                        remapping={'gripper_id': 'gripper_id', 'screw_status_list': 'list_gripper_screws_status'})

            # x:195 y:405
            OperatableStateMachine.add('log_err_screws',
                                        LogKeyState(text="GEC: Fail with available screws: {}", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'error'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'data': 'error_reason'})

            # x:851 y:275
            OperatableStateMachine.add('set_use_another_gripper',
                                        CalculationState(calculation=lambda x: False),
                                        transitions={'done': 'gripper_terminated'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'input_value': 'use_same_gripper', 'output_value': 'use_same_gripper'})

            # x:1159 y:189
            OperatableStateMachine.add('set_use_same_gripper',
                                        CalculationState(calculation=lambda x: True),
                                        transitions={'done': 'Available Screw In current Gripper'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'input_value': 'use_same_gripper', 'output_value': 'use_same_gripper'})

            # x:224 y:62
            OperatableStateMachine.add('wait_screw_update',
                                        WaitState(wait_time=2),
                                        transitions={'done': 'get_screw_in_gripper'},
                                        autonomy={'done': Autonomy.Off})

            # x:1384 y:220
            OperatableStateMachine.add('Available Screw In current Gripper',
                                        PartAvailablePoseService(check_only_current_gripper=True),
                                        transitions={'succeeded': 'screws_available_same_gripper', 'aborted': 'operator_check'},
                                        autonomy={'succeeded': Autonomy.Off, 'aborted': Autonomy.Off},
                                        remapping={'last_trajectory_id': 'next_trajectory', 'list_available_parts': 'list_available_screw_poses'})


        # x:611 y:158
        _sm_log_screws_5 = OperatableStateMachine(outcomes=['done'], input_keys=['screw_found', 'insertion_successful', 'next_trajectory'])

        with _sm_log_screws_5:
            # x:79 y:175
            OperatableStateMachine.add('log_screw_id',
                                        LogKeyState(text="GCE-ENTER: insterd screw id {}", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'log_last_insertion'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'data': 'next_trajectory'})

            # x:423 y:441
            OperatableStateMachine.add('log_screw_found',
                                        LogKeyState(text="GCE-ENTER: screw was found ? {}", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'done'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'data': 'screw_found'})

            # x:217 y:276
            OperatableStateMachine.add('log_last_insertion',
                                        LogKeyState(text="GCE-ENTER: last insertion was succesfu? {}", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'log_screw_found'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'data': 'insertion_successful'})


        # x:422 y:304, x:170 y:189
        _sm_fix_for_screwed_but_not_found_6 = OperatableStateMachine(outcomes=['found_and_inserted', 'not_inserted'], input_keys=['screw_found', 'screw_inserted'], output_keys=['screw_found'])

        with _sm_fix_for_screwed_but_not_found_6:
            # x:156 y:37
            OperatableStateMachine.add('Check is Inserted',
                                        CheckConditionState(predicate=lambda x: x == True),
                                        transitions={'true': 'check is found', 'false': 'not_inserted'},
                                        autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                        remapping={'input_value': 'screw_inserted'})

            # x:287 y:127
            OperatableStateMachine.add('check is found',
                                        CheckConditionState(predicate=lambda x: x == True),
                                        transitions={'true': 'found_and_inserted', 'false': 'fix for inserted not found'},
                                        autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                        remapping={'input_value': 'screw_found'})

            # x:511 y:219
            OperatableStateMachine.add('fix for inserted not found',
                                        CalculationState(calculation=lambda x : True),
                                        transitions={'done': 'found_and_inserted'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'input_value': 'screw_found', 'output_value': 'screw_found'})


        # x:30 y:538, x:768 y:326, x:230 y:538, x:778 y:631, x:480 y:434
        _sm_ask_once_for_retry_7 = OperatableStateMachine(outcomes=['error', 'retry', 'skip', 'confrimed_inserted', 'abort_gripper'], input_keys=['next_trajectory', 'interact_screw_failed'])

        with _sm_ask_once_for_retry_7:
            # x:36 y:29
            OperatableStateMachine.add('utter_not_inserted_text',
                                        LisaMotekConcatenateScrewPartString(text_format="The {} has failed the insertion: select to retry, or skip the screw, or abort the whole gripper", number_part_screws=4),
                                        transitions={'done': 'utter'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'screw_id': 'next_trajectory', 'text_to_utter': 'text_to_utter'})

            # x:454 y:522
            OperatableStateMachine.add('check_abort_gripper',
                                        CheckConditionState(predicate=lambda x: x=='abort_gripper'),
                                        transitions={'true': 'abort_gripper', 'false': 'skip'},
                                        autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                        remapping={'input_value': 'intent_recognized'})

            # x:747 y:508
            OperatableStateMachine.add('check_confirm',
                                        CheckConditionState(predicate=lambda x: x=='confirm'),
                                        transitions={'true': 'confrimed_inserted', 'false': 'check_abort_gripper'},
                                        autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                        remapping={'input_value': 'intent_recognized'})

            # x:975 y:166
            OperatableStateMachine.add('check_retry',
                                        CheckConditionState(predicate=lambda x: x=='retry'),
                                        transitions={'true': 'retry', 'false': 'check_confirm'},
                                        autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                        remapping={'input_value': 'intent_recognized'})

            # x:714 y:30
            OperatableStateMachine.add('log_recogn',
                                        LogKeyState(text="recognized: {}", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'wait_recogn'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'data': 'intent_recognized'})

            # x:540 y:145
            OperatableStateMachine.add('log_to',
                                        LogState(text="TIMEOUT !!!", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'wait_to'},
                                        autonomy={'done': Autonomy.Off})

            # x:41 y:138
            OperatableStateMachine.add('utter',
                                        LisaUtterActionStateWithUserkey(wait_time=0),
                                        transitions={'uttered_all': 'ask_retry_2', 'timeout': 'ask_retry_2', 'command_error': 'error'},
                                        autonomy={'uttered_all': Autonomy.Off, 'timeout': Autonomy.Off, 'command_error': Autonomy.Off},
                                        remapping={'text_to_utter': 'text_to_utter', 'error_reason': 'error_reason'})

            # x:859 y:59
            OperatableStateMachine.add('wait_recogn',
                                        WaitState(wait_time=0.1),
                                        transitions={'done': 'check_retry'},
                                        autonomy={'done': Autonomy.Off})

            # x:681 y:228
            OperatableStateMachine.add('wait_to',
                                        WaitState(wait_time=2),
                                        transitions={'done': 'check_retry'},
                                        autonomy={'done': Autonomy.Off})

            # x:394 y:29
            OperatableStateMachine.add('ask_retry_2',
                                        LisaUtterAndWaitForIntentState(context_id=None, intents=['retry','skip', 'abort_gripper'], wait_time=0),
                                        transitions={'intent_recognized': 'log_recogn', 'intent_not_recognized': 'skip', 'preempt': 'skip', 'timeouted': 'log_to', 'error': 'error'},
                                        autonomy={'intent_recognized': Autonomy.Off, 'intent_not_recognized': Autonomy.Off, 'preempt': Autonomy.Off, 'timeouted': Autonomy.Off, 'error': Autonomy.Off},
                                        remapping={'text_to_utter': 'interact_screw_failed', 'payload': 'payload', 'original_sentence': 'original_sentence', 'error_reason': 'error_reason', 'intent_recognized': 'intent_recognized'})


        # x:333 y:404, x:118 y:300, x:1014 y:328, x:601 y:365
        _sm_ask_end_gripper_status_8 = OperatableStateMachine(outcomes=['unknown', 'error', 'incomplete', 'complete'], input_keys=['next_trajectory', 'list_gripper_screws_status'])

        with _sm_ask_end_gripper_status_8:
            # x:30 y:40
            OperatableStateMachine.add('Ask for Gripper Complete',
                                        self.use_behavior(GripperCompleteSM, 'Gripper Ended Check/Ask End Gripper status/Ask for Gripper Complete'),
                                        transitions={'finished': 'log_answer', 'failed': 'log_exit_failed', 'max_retry': 'exit_unknwon'},
                                        autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit, 'max_retry': Autonomy.Inherit},
                                        remapping={'answer': 'answer'})

            # x:558 y:53
            OperatableStateMachine.add('check answer',
                                        CheckConditionState(predicate=lambda x: x == "yes" or x == "completed"),
                                        transitions={'true': 'complete', 'false': 'reset_gripper'},
                                        autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                        remapping={'input_value': 'answer'})

            # x:1134 y:90
            OperatableStateMachine.add('exit_reset',
                                        LogState(text="DBG-EXIT: incomplete, gripper resetted", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'incomplete'},
                                        autonomy={'done': Autonomy.Off})

            # x:405 y:281
            OperatableStateMachine.add('exit_unknwon',
                                        LogState(text="DBG-EXIT: unknwon, exit NOT resetted", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'unknown'},
                                        autonomy={'done': Autonomy.Off})

            # x:370 y:40
            OperatableStateMachine.add('log_answer',
                                        LogKeyState(text="GCE: User reply {}", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'check answer'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'data': 'answer'})

            # x:124 y:171
            OperatableStateMachine.add('log_exit_failed',
                                        LogState(text="GCE: exit failed", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'error'},
                                        autonomy={'done': Autonomy.Off})

            # x:776 y:90
            OperatableStateMachine.add('reset_gripper',
                                        ResetScrewStatesInGripper(number_part_screws=4),
                                        transitions={'succeeded': 'exit_reset', 'aborted': 'error', 'nothing_to_do': 'complete'},
                                        autonomy={'succeeded': Autonomy.Off, 'aborted': Autonomy.Off, 'nothing_to_do': Autonomy.Off},
                                        remapping={'screw_id': 'next_trajectory', 'screw_status_list': 'list_gripper_screws_status', 'result': 'result', 'reason': 'reason'})


        # x:1037 y:610, x:970 y:180, x:834 y:157, x:1315 y:92, x:1713 y:466
        _sm_gripper_ended_check_9 = OperatableStateMachine(outcomes=['fail', 'completed', 'screw_available', 'incomplete', 'unknown'], input_keys=['next_trajectory', 'insertion_successful', 'screw_found', 'use_same_gripper', 'interact_screw_failed'], output_keys=['list_available_screw_poses', 'use_same_gripper'])

        with _sm_gripper_ended_check_9:
            # x:71 y:86
            OperatableStateMachine.add('Fix for screwed but not found',
                                        _sm_fix_for_screwed_but_not_found_6,
                                        transitions={'found_and_inserted': 'Update Screw', 'not_inserted': 'Ask Once for retry'},
                                        autonomy={'found_and_inserted': Autonomy.Inherit, 'not_inserted': Autonomy.Inherit},
                                        remapping={'screw_found': 'screw_found', 'screw_inserted': 'insertion_successful'})

            # x:272 y:460
            OperatableStateMachine.add('Ask Once for retry',
                                        _sm_ask_once_for_retry_7,
                                        transitions={'error': 'fail', 'retry': 'utter_retry', 'skip': 'Update Screw', 'confrimed_inserted': 'set_screw_inserted', 'abort_gripper': 'set_change_gripper'},
                                        autonomy={'error': Autonomy.Inherit, 'retry': Autonomy.Inherit, 'skip': Autonomy.Inherit, 'confrimed_inserted': Autonomy.Inherit, 'abort_gripper': Autonomy.Inherit},
                                        remapping={'next_trajectory': 'next_trajectory', 'interact_screw_failed': 'interact_screw_failed'})

            # x:92 y:255
            OperatableStateMachine.add('Log screws',
                                        _sm_log_screws_5,
                                        transitions={'done': 'Fix for screwed but not found'},
                                        autonomy={'done': Autonomy.Inherit},
                                        remapping={'screw_found': 'screw_found', 'insertion_successful': 'insertion_successful', 'next_trajectory': 'next_trajectory'})

            # x:491 y:12
            OperatableStateMachine.add('Update Screw',
                                        _sm_update_screw_4,
                                        transitions={'operator_check': 'Ask End Gripper status', 'error': 'fail', 'gripper_terminated': 'utter_completed', 'screws_available_same_gripper': 'utter_next_traj', 'missing_screws': 'utter_missing_screw'},
                                        autonomy={'operator_check': Autonomy.Inherit, 'error': Autonomy.Inherit, 'gripper_terminated': Autonomy.Inherit, 'screws_available_same_gripper': Autonomy.Inherit, 'missing_screws': Autonomy.Inherit},
                                        remapping={'use_same_gripper': 'use_same_gripper', 'next_trajectory': 'next_trajectory', 'insertion_successful': 'insertion_successful', 'screw_found': 'screw_found', 'list_gripper_screws_status': 'list_gripper_screws_status', 'list_available_screw_poses': 'list_available_screw_poses'})

            # x:496 y:394
            OperatableStateMachine.add('set_change_gripper',
                                        CalculationState(calculation=lambda  x: False),
                                        transitions={'done': 'utter_aborted'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'input_value': 'use_same_gripper', 'output_value': 'use_same_gripper'})

            # x:514 y:148
            OperatableStateMachine.add('set_screw_inserted',
                                        CalculationState(calculation=lambda x: True),
                                        transitions={'done': 'Update Screw'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'input_value': 'insertion_successful', 'output_value': 'insertion_successful'})

            # x:562 y:306
            OperatableStateMachine.add('utter_aborted',
                                        LisaUtterActionState(text_to_utter="Present gripper aborted", wait_time=0),
                                        transitions={'uttered_all': 'unknown', 'timeout': 'unknown', 'command_error': 'fail'},
                                        autonomy={'uttered_all': Autonomy.Off, 'timeout': Autonomy.Off, 'command_error': Autonomy.Off},
                                        remapping={'error_reason': 'error_reason'})

            # x:864 y:50
            OperatableStateMachine.add('utter_completed',
                                        LisaUtterActionState(text_to_utter=utter_complete, wait_time=0),
                                        transitions={'uttered_all': 'completed', 'timeout': 'completed', 'command_error': 'fail'},
                                        autonomy={'uttered_all': Autonomy.Off, 'timeout': Autonomy.Off, 'command_error': Autonomy.Off},
                                        remapping={'error_reason': 'error_reason'})

            # x:1610 y:23
            OperatableStateMachine.add('utter_exit_not_complete',
                                        LisaUtterActionState(text_to_utter=utter_incomplete, wait_time=0),
                                        transitions={'uttered_all': 'incomplete', 'timeout': 'incomplete', 'command_error': 'fail'},
                                        autonomy={'uttered_all': Autonomy.Off, 'timeout': Autonomy.Off, 'command_error': Autonomy.Off},
                                        remapping={'error_reason': 'error_reason'})

            # x:1167 y:225
            OperatableStateMachine.add('utter_missing_screw',
                                        LisaUtterActionState(text_to_utter="One ore more screws are  not available", wait_time=0),
                                        transitions={'uttered_all': 'incomplete', 'timeout': 'incomplete', 'command_error': 'fail'},
                                        autonomy={'uttered_all': Autonomy.Off, 'timeout': Autonomy.Off, 'command_error': Autonomy.Off},
                                        remapping={'error_reason': 'error_reason'})

            # x:838 y:227
            OperatableStateMachine.add('utter_next_traj',
                                        LisaUtterActionState(text_to_utter=utter_next_screw, wait_time=0),
                                        transitions={'uttered_all': 'screw_available', 'timeout': 'screw_available', 'command_error': 'fail'},
                                        autonomy={'uttered_all': Autonomy.Off, 'timeout': Autonomy.Off, 'command_error': Autonomy.Off},
                                        remapping={'error_reason': 'error_reason'})

            # x:525 y:230
            OperatableStateMachine.add('utter_retry',
                                        LisaUtterActionState(text_to_utter="retry the same screw", wait_time=0),
                                        transitions={'uttered_all': 'screw_available', 'timeout': 'screw_available', 'command_error': 'fail'},
                                        autonomy={'uttered_all': Autonomy.Off, 'timeout': Autonomy.Off, 'command_error': Autonomy.Off},
                                        remapping={'error_reason': 'error_reason'})

            # x:1641 y:290
            OperatableStateMachine.add('utter_unknown',
                                        LisaUtterActionState(text_to_utter=utter_unknown, wait_time=0),
                                        transitions={'uttered_all': 'unknown', 'timeout': 'unknown', 'command_error': 'fail'},
                                        autonomy={'uttered_all': Autonomy.Off, 'timeout': Autonomy.Off, 'command_error': Autonomy.Off},
                                        remapping={'error_reason': 'error_reason'})

            # x:1154 y:16
            OperatableStateMachine.add('Ask End Gripper status',
                                        _sm_ask_end_gripper_status_8,
                                        transitions={'unknown': 'utter_unknown', 'error': 'fail', 'incomplete': 'utter_exit_not_complete', 'complete': 'utter_completed'},
                                        autonomy={'unknown': Autonomy.Inherit, 'error': Autonomy.Inherit, 'incomplete': Autonomy.Inherit, 'complete': Autonomy.Inherit},
                                        remapping={'next_trajectory': 'next_trajectory', 'list_gripper_screws_status': 'list_gripper_screws_status'})



        with _state_machine:
            # x:112 y:30
            OperatableStateMachine.add('Load Trajectory',
                                        SharedWsActionState(exec_speed=exec_speed, exec_acceleration=exec_acceleration, coll_threshold=coll_threshold, coll_repeats=coll_repeats),
                                        transitions={'succeeded': 'Move To Home', 'preempted': 'failed', 'aborted': 'failed'},
                                        autonomy={'succeeded': Autonomy.Off, 'preempted': Autonomy.Off, 'aborted': Autonomy.Off},
                                        remapping={'action_id': 'eREAD_FROM_DISK', 'trajectory_id': 'ZERO', 'results': 'results'})

            # x:890 y:186
            OperatableStateMachine.add('MotekInsertScrew',
                                        self.use_behavior(MotekInsertScrewSM, 'MotekInsertScrew'),
                                        transitions={'finished': 'Gripper Ended Check', 'failed': 'failed'},
                                        autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit},
                                        remapping={'velocity': 'velocity', 'insertion_successful': 'insertion_successful', 'screw_found': 'screw_found'})

            # x:334 y:30
            OperatableStateMachine.add('Move To Home',
                                        SharedWsActionState(exec_speed=exec_speed, exec_acceleration=exec_acceleration, coll_threshold=coll_threshold, coll_repeats=coll_repeats),
                                        transitions={'succeeded': 'search and move to next screw', 'preempted': 'failed', 'aborted': 'failed'},
                                        autonomy={'succeeded': Autonomy.Off, 'preempted': Autonomy.Off, 'aborted': Autonomy.Off},
                                        remapping={'action_id': 'eDRIVE_TO_START', 'trajectory_id': 'ZERO', 'results': 'results'})

            # x:756 y:374
            OperatableStateMachine.add('log_avail_screws',
                                        LogKeyState(text="MAIN: available screws \n{}", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'Gripper Ended Check'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'data': 'list_available_screw_poses'})

            # x:237 y:214
            OperatableStateMachine.add('log_completed',
                                        LogKeyState(text="MAIN: Gripper complete, use_same_gripper={}", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'Move To Home'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'data': 'use_same_gripper'})

            # x:523 y:123
            OperatableStateMachine.add('log_uncomplete',
                                        LogKeyState(text="MAIN: Gripper uncomplete, use_same_gripper={}", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'search and move to next screw'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'data': 'use_same_gripper'})

            # x:385 y:220
            OperatableStateMachine.add('log_unknown',
                                        LogKeyState(text="gripper is unknown {}", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'Move To Home'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'data': 'use_same_gripper'})

            # x:599 y:216
            OperatableStateMachine.add('screw_available',
                                        LogKeyState(text="Availavke screw same gripper, use_same_gripper={}", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'search and move to next screw'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'data': 'use_same_gripper'})

            # x:716 y:23
            OperatableStateMachine.add('search and move to next screw',
                                        _sm_search_and_move_to_next_screw_3,
                                        transitions={'error': 'failed', 'moved_to_next_screw': 'MotekInsertScrew'},
                                        autonomy={'error': Autonomy.Inherit, 'moved_to_next_screw': Autonomy.Inherit},
                                        remapping={'eEXECUTE_NEW_TRAJ': 'eEXECUTE_NEW_TRAJ', 'eCREATE_NEW_TRAJ': 'eCREATE_NEW_TRAJ', 'next_trajectory': 'next_trajectory', 'list_available_screw_poses': 'list_available_screw_poses', 'use_same_gripper': 'use_same_gripper', 'same_gripper_retry': 'same_gripper_retry', 'obstacle_traj_counter': 'obstacle_traj_counter'})

            # x:362 y:383
            OperatableStateMachine.add('Gripper Ended Check',
                                        _sm_gripper_ended_check_9,
                                        transitions={'fail': 'failed', 'completed': 'log_completed', 'screw_available': 'screw_available', 'incomplete': 'log_uncomplete', 'unknown': 'log_unknown'},
                                        autonomy={'fail': Autonomy.Inherit, 'completed': Autonomy.Inherit, 'screw_available': Autonomy.Inherit, 'incomplete': Autonomy.Inherit, 'unknown': Autonomy.Inherit},
                                        remapping={'next_trajectory': 'next_trajectory', 'insertion_successful': 'insertion_successful', 'screw_found': 'screw_found', 'use_same_gripper': 'use_same_gripper', 'interact_screw_failed': 'interact_screw_failed', 'list_available_screw_poses': 'list_available_screw_poses'})


        return _state_machine


    # Private functions can be added inside the following tags
    # [MANUAL_FUNC]

    # [/MANUAL_FUNC]
