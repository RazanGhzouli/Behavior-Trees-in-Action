#!/usr/bin/env python
#-*- coding: utf-8 -*-
import sys
import rospy
import smach
import smach_ros
from std_msgs.msg import String
from mimi_common_pkg.srv import ManipulateSrv
from navi_location.srv import NaviLocation

sys.path.insert(0,'/home/athome/catkin_ws/src/mimi_common_pkg/scripts')
from common_action_client import *
from common_function import *
sys.path.insert(0, '/home/athome/catkin_ws/src/mimi_voice_control/src')
from voice_common_pkg.srv import WhatDidYousay

class TASK(smach.State):
    def __init__(self):
        smach.State.__init__(self,
                             outcomes = ['outcome1','outcome2'],
                             input_keys = ['task_counter_in'],
                             output_keys = ['task_counter_out'])
        self.grab = rospy.ServiceProxy('/manipulation',ManipulateSrv)
        self.navi_location = rospy.ServiceProxy('navi_location_server',NaviLcation)
        self.arm_srv = rospy.ServiceProxy('/servo/arm',ManipulateSrv
        self.stt_pub = rospyServiceProxy('/speech_recog',SpeechRecog)

    def execute(self, userdata):
        rospy.loginfo('Executing state=> TASK')
        speak('may I start task1?')
        result = self.stt_pub().result
        if result == 'yes':
            if userdata.task_counter_in == 1:
                print 'task1 start'
                userdata.task_counter_out = userdata.task_counter_in + 1
                enterTheRoomAC(0.8)
                self.navi_location('Long table A')
                while not rospy.is_shutdown():
                    result1 = self.grab('cup').result
                    if result1 == False:
                        break
                    else:
                        self.navi_location('Bookshelf')
                        self.arm_srv('place')
                        self.navi_location('Long table B')
                while not rospy.is_shutdown():
                    result2 = self.grab('bottle').result
                    if result2 == False:
                        break
                    else:
                        self.navi_location('Bookshelf')
                        self.arm_srv('place')
                        self.navi_locationf('Long table B')
                return 'outcome2'
                        

            if userdata.task_counter_in == 2:
                print 'task2 start'
                self.navi_location('Chair A')
                speak('what should I bring up')
                result3 = self.stt_pub().result
                speak('ok I bring up')
                self.navi_location('Bookshelf')
                self.grab('result')
                self.navi_location('Chair A')
                self.arm_srv('give')
                return 'outcome1'
        else:
            return 'outcome2'
                
                

        


                    

def main():
    rospy.init_node('wrs_task_practice')
    sm = smach.StateMachine(outcomes = ['task_finish'])
    sm.userdata.sm_counter = 1
    with sm:
        smach.StateMachine.add('TASK',TASK(),
                               transitions={'outcome1':'task_finish',
                                            'outcome2':'TASK'},
                               remapping={'task_counter_in':'sm_counter',
                                          'task_counter_out':'sm_counter'}) 

    outcome = sm.execute()

if __name__ == '__main__':
    main()
