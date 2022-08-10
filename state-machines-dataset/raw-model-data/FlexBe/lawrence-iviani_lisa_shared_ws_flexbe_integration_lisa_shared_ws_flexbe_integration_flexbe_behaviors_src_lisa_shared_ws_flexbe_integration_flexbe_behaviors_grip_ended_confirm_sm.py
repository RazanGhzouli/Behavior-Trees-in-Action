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
from flexbe_states.wait_state import WaitState
from horse_flexbe_states.part_available_pose_service_state import PartAvailablePoseService
from horse_flexbe_states.set_screw_service_state import SetScrewServiceState
from lisa_flexbe_states_flexbe_states.lisa_extract_payload_key import LisaGetPayloadKeyState
from lisa_flexbe_states_flexbe_states.lisa_intent_result_to_string import LisaRecognitionResultToStringState
from lisa_flexbe_states_flexbe_states.lisa_utter_and_wait_for_intent_state import LisaUtterAndWaitForIntentState
from lisa_flexbe_states_flexbe_states.lisa_utter_state import LisaUtterState
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]

# [/MANUAL_IMPORT]


'''
Created on Tue Nov 21 2020
@author: Lawrence Iviani
'''
class GripEndedConfirmSM(Behavior):
    '''
    A sub-behaviour in motek 2018, to recognize what to do with gripper and screws.
A state machine to be used in motek 2018 to interact with operators about gripper finalization
    '''


    def __init__(self):
        super(GripEndedConfirmSM, self).__init__()
        self.name = 'Grip Ended Confirm'

        # parameters of this behavior

        # references to used behaviors

        # semantic properties of this behavior
        self._semantic_properties = {}

        # Additional initialization code can be added inside the following tags
        # [MANUAL_INIT]
        
        # [/MANUAL_INIT]

        # Behavior comments:

        # O 784 83 
        # If there are other screws, let him to continue and not bother the operator

        # O 762 508 
        # No reply from the man or some other non fatal issue in the dialog.|nWhich end in an unknown status of the gripper

        # O 180 851 
        # The operator confirmed the gripper is finished

        # O 1476 77 
        # When there are no screws available in the gripper, the exit is in abort status.|nThis mean two things:|nTHe gripper is finished|nThe gripper has not all the screws in it (missing, wrong, not screwed etc.) but it is not done. User must recognize it



    def create(self):
        wait_for_confirm = 25
        wait_for_utter = 15
        intents = ['YesNo', 'Complete', 'ConfirmGripperFinished']
        answer = 'part_type'
        detail_levels = 'low'
        confirm_key = 'answer'
        wait_before_exit = 2
        session_id = None
        # x:143 y:908, x:539 y:365, x:546 y:667, x:755 y:635, x:860 y:350, x:668 y:414
        _state_machine = OperatableStateMachine(outcomes=['complete', 'incomplete', 'fail', 'unknwon', 'aborted', 'succeded'], input_keys=['screw_id', 'screw_found', 'last_insert_finished_successful'], output_keys=['list_available_screw_poses', 'confirmed'])
        _state_machine.userdata.gripper_ended_question = 'Is the gripper complete?'
        _state_machine.userdata.answer = ''
        _state_machine.userdata.retry = 2
        _state_machine.userdata.list_available_screw_poses = []
        _state_machine.userdata.next_trajectory = -1
        _state_machine.userdata.screw_id = 0
        _state_machine.userdata.screw_found = 0
        _state_machine.userdata.last_insert_finished_successful = True
        _state_machine.userdata.confirmed = ''
        _state_machine.userdata.utter_abort_screw_state = 'Error in the update of the screw state, aborting'

        # Additional creation code can be added inside the following tags
        # [MANUAL_CREATE]
        
        # [/MANUAL_CREATE]

        # x:30 y:373, x:385 y:382
        _sm_continueretry_0 = OperatableStateMachine(outcomes=['true', 'false'], input_keys=['retry'], output_keys=['retry'])

        with _sm_continueretry_0:
            # x:158 y:82
            OperatableStateMachine.add('decrease_retry',
                                        CalculationState(calculation=lambda x: x-1),
                                        transitions={'done': 'continue_asking'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'input_value': 'retry', 'output_value': 'retry'})

            # x:156 y:221
            OperatableStateMachine.add('continue_asking',
                                        CheckConditionState(predicate=lambda x: x > 0),
                                        transitions={'true': 'true', 'false': 'false'},
                                        autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                        remapping={'input_value': 'retry'})



        with _state_machine:
            # x:25 y:35
            OperatableStateMachine.add('log_insert_success',
                                        LogKeyState(text="GEC-ENTER: last insertion was succesful? {}", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'log_screw_id'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'data': 'last_insert_finished_successful'})

            # x:1069 y:524
            OperatableStateMachine.add('ContinueRetry',
                                        _sm_continueretry_0,
                                        transitions={'true': 'log_retry_value', 'false': 'wait_unknown'},
                                        autonomy={'true': Autonomy.Inherit, 'false': Autonomy.Inherit},
                                        remapping={'retry': 'retry'})

            # x:104 y:685
            OperatableStateMachine.add('GetConfirm',
                                        LisaGetPayloadKeyState(payload_key=confirm_key),
                                        transitions={'done': 'wait_complete', 'error': 'fail'},
                                        autonomy={'done': Autonomy.Off, 'error': Autonomy.Off},
                                        remapping={'payload': 'payload', 'payload_value': 'confirmed'})

            # x:1304 y:483
            OperatableStateMachine.add('NotRecognized',
                                        LisaRecognitionResultToStringState(context_id=session_id, detail_levels=detail_levels),
                                        transitions={'done': 'UtterRecognizedText'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'payload': 'payload', 'original_sentence': 'original_sentence', 'error_reason': 'error_reason', 'intent_recognized': 'intent_recognized', 'text_to_utter': 'text_to_utter'})

            # x:52 y:376
            OperatableStateMachine.add('Recognized',
                                        LisaRecognitionResultToStringState(context_id=session_id, detail_levels=detail_levels),
                                        transitions={'done': 'UtterRecognized'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'payload': 'payload', 'original_sentence': 'original_sentence', 'error_reason': 'error_reason', 'intent_recognized': 'intent_recognized', 'text_to_utter': 'text_to_utter'})

            # x:49 y:134
            OperatableStateMachine.add('Update Screw State',
                                        SetScrewServiceState(),
                                        transitions={'succeeded': 'Update Success', 'aborted': 'Utter Error Update Screw State'},
                                        autonomy={'succeeded': Autonomy.Off, 'aborted': Autonomy.Off},
                                        remapping={'screw_id': 'screw_id', 'finished_successful': 'last_insert_finished_successful', 'screw_found': 'screw_found', 'result': 'result'})

            # x:380 y:87
            OperatableStateMachine.add('Update Success',
                                        LogKeyState(text="GEC: Update Screw State returned: {}", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'Valid Screw In Current Gripper'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'data': 'result'})

            # x:355 y:155
            OperatableStateMachine.add('Utter Error Update Screw State',
                                        LisaUtterState(context_id=session_id, wait_time=15, suspend_time=0),
                                        transitions={'done': 'fail', 'preempt': 'fail', 'timeouted': 'fail', 'error': 'fail'},
                                        autonomy={'done': Autonomy.Off, 'preempt': Autonomy.Off, 'timeouted': Autonomy.Off, 'error': Autonomy.Off},
                                        remapping={'text_to_utter': 'utter_abort_screw_state', 'error_reason': 'error_reason'})

            # x:74 y:542
            OperatableStateMachine.add('UtterRecognized',
                                        LisaUtterState(context_id=None, wait_time=wait_for_utter, suspend_time=0),
                                        transitions={'done': 'GetConfirm', 'preempt': 'GetConfirm', 'timeouted': 'GetConfirm', 'error': 'fail'},
                                        autonomy={'done': Autonomy.Off, 'preempt': Autonomy.Off, 'timeouted': Autonomy.Off, 'error': Autonomy.Off},
                                        remapping={'text_to_utter': 'text_to_utter', 'error_reason': 'error_reason'})

            # x:1104 y:747
            OperatableStateMachine.add('UtterRecognizedText',
                                        LisaUtterState(context_id=session_id, wait_time=wait_for_utter, suspend_time=0),
                                        transitions={'done': 'ContinueRetry', 'preempt': 'wait_unknown', 'timeouted': 'wait_unknown', 'error': 'fail'},
                                        autonomy={'done': Autonomy.Off, 'preempt': Autonomy.Off, 'timeouted': Autonomy.Off, 'error': Autonomy.Off},
                                        remapping={'text_to_utter': 'text_to_utter', 'error_reason': 'error_reason'})

            # x:545 y:26
            OperatableStateMachine.add('Valid Screw In Current Gripper',
                                        PartAvailablePoseService(check_only_current_gripper=True),
                                        transitions={'succeeded': 'succeded', 'aborted': 'aborted'},
                                        autonomy={'succeeded': Autonomy.Off, 'aborted': Autonomy.Off},
                                        remapping={'last_trajectory_id': 'screw_id', 'list_available_parts': 'list_available_screw_poses'})

            # x:768 y:137
            OperatableStateMachine.add('log_exit_incomplete',
                                        LogKeyState(text="GEC-EXIT-INCOMPLETE {}", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'wait_before_incomplete'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'data': 'list_available_screw_poses'})

            # x:1126 y:350
            OperatableStateMachine.add('log_retry_value',
                                        LogKeyState(text="GEC: retry level is {}", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'AskGripperEneded'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'data': 'retry'})

            # x:308 y:28
            OperatableStateMachine.add('log_screw_found',
                                        LogKeyState(text="GEC-ENTER: I found the latest screw? {}", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'Update Screw State'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'data': 'screw_found'})

            # x:193 y:36
            OperatableStateMachine.add('log_screw_id',
                                        LogKeyState(text="GEC-ENTER: latest screw id was: {}", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'log_screw_found'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'data': 'screw_id'})

            # x:589 y:148
            OperatableStateMachine.add('wait_before_incomplete',
                                        WaitState(wait_time=wait_before_exit),
                                        transitions={'done': 'incomplete'},
                                        autonomy={'done': Autonomy.Off})

            # x:109 y:774
            OperatableStateMachine.add('wait_complete',
                                        WaitState(wait_time=wait_before_exit),
                                        transitions={'done': 'complete'},
                                        autonomy={'done': Autonomy.Off})

            # x:857 y:592
            OperatableStateMachine.add('wait_unknown',
                                        WaitState(wait_time=wait_before_exit),
                                        transitions={'done': 'unknwon'},
                                        autonomy={'done': Autonomy.Off})

            # x:1271 y:115
            OperatableStateMachine.add('AskGripperEneded',
                                        LisaUtterAndWaitForIntentState(context_id=session_id, intents=intents, wait_time=wait_for_confirm),
                                        transitions={'intent_recognized': 'Recognized', 'intent_not_recognized': 'NotRecognized', 'preempt': 'wait_unknown', 'timeouted': 'wait_unknown', 'error': 'fail'},
                                        autonomy={'intent_recognized': Autonomy.Off, 'intent_not_recognized': Autonomy.Off, 'preempt': Autonomy.Off, 'timeouted': Autonomy.Off, 'error': Autonomy.Off},
                                        remapping={'text_to_utter': 'gripper_ended_question', 'payload': 'payload', 'original_sentence': 'original_sentence', 'error_reason': 'error_reason', 'intent_recognized': 'intent_recognized'})


        return _state_machine


    # Private functions can be added inside the following tags
    # [MANUAL_FUNC]
    
    # [/MANUAL_FUNC]
