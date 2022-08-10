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
from lisa_flexbe_states_flexbe_states.lisa_extract_payload_key import LisaGetPayloadKeyState
from lisa_flexbe_states_flexbe_states.lisa_intent_result_to_string import LisaRecognitionResultToStringState
from lisa_flexbe_states_flexbe_states.lisa_utter_and_wait_for_intent_state import LisaUtterAndWaitForIntentState
from lisa_flexbe_states_flexbe_states.lisa_utter_state import LisaUtterState
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]

# [/MANUAL_IMPORT]


'''
Created on Tue Nov 11 2020
@author: Lawrence Iviani
'''
class GripperCompleteSM(Behavior):
    '''
    A yes No dialogue, to infer from the operator if the gripper is complete
    '''


    def __init__(self):
        super(GripperCompleteSM, self).__init__()
        self.name = 'Gripper Complete'

        # parameters of this behavior

        # references to used behaviors

        # semantic properties of this behavior
        self._semantic_properties = {}

        # Additional initialization code can be added inside the following tags
        # [MANUAL_INIT]
        
        # [/MANUAL_INIT]

        # Behavior comments:

        # O 316 193 
        # used for debug



    def create(self):
        session_id = None
        wait_for_question = 25
        wait_for_utter = 15
        intents = ['YesNo', 'Complete']
        answer_key = 'confirm'
        detail_levels = 'low'
        # x:73 y:608, x:539 y:365, x:575 y:287
        _state_machine = OperatableStateMachine(outcomes=['finished', 'failed', 'max_retry'], output_keys=['answer'])
        _state_machine.userdata.question = 'Please, is the gripper complete?'
        _state_machine.userdata.retry = 2
        _state_machine.userdata.answer = ''

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
            # x:416 y:26
            OperatableStateMachine.add('AskForComplete',
                                        LisaUtterAndWaitForIntentState(context_id=session_id, intents=intents, wait_time=wait_for_question),
                                        transitions={'intent_recognized': 'Recognized', 'intent_not_recognized': 'NotRecognized', 'preempt': 'failed', 'timeouted': 'failed', 'error': 'failed'},
                                        autonomy={'intent_recognized': Autonomy.Off, 'intent_not_recognized': Autonomy.Off, 'preempt': Autonomy.Off, 'timeouted': Autonomy.Off, 'error': Autonomy.Off},
                                        remapping={'text_to_utter': 'question', 'payload': 'payload', 'original_sentence': 'original_sentence', 'error_reason': 'error_reason', 'intent_recognized': 'intent_recognized'})

            # x:690 y:190
            OperatableStateMachine.add('ContinueRetry',
                                        _sm_continueretry_0,
                                        transitions={'true': 'log_retry_value', 'false': 'max_retry'},
                                        autonomy={'true': Autonomy.Inherit, 'false': Autonomy.Inherit},
                                        remapping={'retry': 'retry'})

            # x:52 y:390
            OperatableStateMachine.add('GetAnswerKey',
                                        LisaGetPayloadKeyState(payload_key=answer_key),
                                        transitions={'done': 'log_output', 'error': 'failed'},
                                        autonomy={'done': Autonomy.Off, 'error': Autonomy.Off},
                                        remapping={'payload': 'payload', 'payload_value': 'answer'})

            # x:783 y:27
            OperatableStateMachine.add('NotRecognized',
                                        LisaRecognitionResultToStringState(context_id=session_id, detail_levels=detail_levels),
                                        transitions={'done': 'UtterNotRecognizedText'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'payload': 'payload', 'original_sentence': 'original_sentence', 'error_reason': 'error_reason', 'intent_recognized': 'intent_recognized', 'text_to_utter': 'text_to_utter'})

            # x:42 y:122
            OperatableStateMachine.add('Recognized',
                                        LisaRecognitionResultToStringState(context_id=session_id, detail_levels=detail_levels),
                                        transitions={'done': 'GetAnswerKey'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'payload': 'payload', 'original_sentence': 'original_sentence', 'error_reason': 'error_reason', 'intent_recognized': 'intent_recognized', 'text_to_utter': 'text_to_utter'})

            # x:878 y:289
            OperatableStateMachine.add('UtterNotRecognizedText',
                                        LisaUtterState(context_id=session_id, wait_time=wait_for_utter, suspend_time=1),
                                        transitions={'done': 'ContinueRetry', 'preempt': 'failed', 'timeouted': 'failed', 'error': 'failed'},
                                        autonomy={'done': Autonomy.Off, 'preempt': Autonomy.Off, 'timeouted': Autonomy.Off, 'error': Autonomy.Off},
                                        remapping={'text_to_utter': 'text_to_utter', 'error_reason': 'error_reason'})

            # x:278 y:216
            OperatableStateMachine.add('UtterRecognized',
                                        LisaUtterState(context_id=session_id, wait_time=wait_for_utter, suspend_time=1),
                                        transitions={'done': 'GetAnswerKey', 'preempt': 'failed', 'timeouted': 'failed', 'error': 'failed'},
                                        autonomy={'done': Autonomy.Off, 'preempt': Autonomy.Off, 'timeouted': Autonomy.Off, 'error': Autonomy.Off},
                                        remapping={'text_to_utter': 'text_to_utter', 'error_reason': 'error_reason'})

            # x:74 y:506
            OperatableStateMachine.add('log_output',
                                        LogKeyState(text="GC: exit with answer: {}", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'finished'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'data': 'answer'})

            # x:646 y:73
            OperatableStateMachine.add('log_retry_value',
                                        LogKeyState(text="GC: retry level is {}", severity=Logger.REPORT_HINT),
                                        transitions={'done': 'AskForComplete'},
                                        autonomy={'done': Autonomy.Off},
                                        remapping={'data': 'retry'})


        return _state_machine


    # Private functions can be added inside the following tags
    # [MANUAL_FUNC]
    
    # [/MANUAL_FUNC]
