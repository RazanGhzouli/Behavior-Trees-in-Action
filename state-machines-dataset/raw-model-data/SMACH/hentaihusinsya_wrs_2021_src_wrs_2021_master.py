#!/usr/bin/env python
#-*- coding: utf-8 -*-
#--------------------------------------------
#Title:ゴミを拾って捨てるタスク
#Author: myoujin yuusuke
#--------------------------------------------
import sys
import rospy
import smach
import smach_ros
from std_msgs.msg import String
from mimi_common_pkg.srv import ManipulateSrv
from navi_location.srv import NaviLocation

sys.path.insert(0, '/home/athome/catkin_ws/src/mimi_common_pkg/scripts')
from common_action_client import *
from common_function import *

class OBS(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['outcome1'])
        self.navi_location = rospy.ServiceProxy('navi_location_server',NaviLocation)
        self.grab = rospy.ServiceProxy('/manipulation', ManipulateSrv)
        self.arm_srv = rospy.ServiceProxy('/servo/arm', ManipulateSrv)
        self.obj_search = rospy.ServiceProxy('/recognize/count',RecognazeCount)
    def execute(self, userdata):
        rospy.loginfo('Executing state=>OBS')
        print 'OBS finish'
        self.navi_location('table(仮)')
        self.grab('cup')
        self.navi_location('garbage box')
        self.arm_srv('place')
        return 'outcome1'
    
 





def main():
    rospy.init_node('smach_example_state_machine')

    sm = smach.StateMachine(outcomes=['outcome4'])

    #Open the container
    with sm:
        # Add states to the container
        smach.StateMachine.add('OBS',OBS(),transitions = {'outcome1': 'outcome4'})
        
    #Execute SMACH plan
    outcome  = sm.execute()

if __name__ == '__main__':
    main()

