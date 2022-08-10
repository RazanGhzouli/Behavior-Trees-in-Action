#!/usr/bin/env python
import rospy
import sys
import time
from os.path import dirname

sys.path.append((dirname(dirname(__file__))))

import smach
import smach_ros
from lane_vision import LaneDetector
from lane_comm import LaneComms
from utils.common import *

class Disengage(smach.State):

    def __init__(self, laner):
        smach.State.__init__(self, outcomes=['started', 'aborted', 'done'])
        self.laner = laner
        self.comm = laner.comm

    def execute(self, userdata):

        if self.comm.isKilled:
            return 'aborted'

        if self.comm.debug == 2:
            self.comm.isAlone = False
            self.comm.missionBridge("/lane/")
            self.comm.register()
            self.comm.debug = 1 #Reset to prevent multiple registration

        while not self.comm.isStart:
            if self.comm.isKilled: 
                return 'aborted'
            rospy.sleep(rospy.Duration(0.1))

        self.comm.time = time.time()
        if self.comm.debug <= 2:
            self.comm.startPID()
        return 'started'


class Find_Lane(smach.State):


    def __init__(self, laner):
        smach.State.__init__(self, outcomes=['found', 'aborted', 'retry'])
        self.laner = laner
        self.comm = laner.comm

    def execute(self, userdata):

        self.comm.detector = VUtil.findLane
        rospy.logerr("FINDING LANE")
        rospy.sleep(rospy.Duration(0.5))

        while not self.comm.isKilled:

            if self.comm.outData.data['detected']:
                deltaX = self.comm.outData.data['dxy'][0]
                deltaY = self.comm.outData.data['dxy'][1]
                angle = self.comm.outData.data['angle']
                rospy.logwarn("dx: %.2f dy: %.2f t: %d" % (deltaX,deltaY,int(angle)))

                if abs(deltaX) <= 0.1 and abs(deltaY) <= 0.1:
                    self.comm.sendMovement(turn=angle)
                    self.comm.isStart = False 
                    self.comm.taskComplete(self.comm.heading)
                    return 'found'

                if abs(deltaX) != 0.2 and abs(deltaY) != 0.2:
                    self.comm.sendMovement(forward=deltaY*2.0, sidemove=deltaX*8.0, wait=False)


        return 'aborted'

if __name__ == '__main__':
    rospy.init_node('laner')
    mode = rospy.get_param('~mode', 2)
    laner = LaneDetector()
    laner.comm = LaneComms('laner', laner.detect, mode)
    rospy.loginfo("Laner loaded!")

    sm = smach.StateMachine(outcomes=['task_complete', 'aborted'])
    with sm:
        smach.StateMachine.add('DISENGAGE', Disengage(laner),
                               transitions={'started' : 'FIND_LANE',
                                   'aborted' : 'aborted', 'done':'task_complete'})

        smach.StateMachine.add('FIND_LANE', Find_Lane(laner),
                               transitions={'found' : 'DISENGAGE',
                                   'aborted' : 'aborted', 'retry':'FIND_LANE'})

    introServer = smach_ros.IntrospectionServer('lane_server',
                                                sm,
                                                '/MISSION/LANE')
    introServer.start()

    try:
        sm.execute()
    except Exception as e:
        rospy.logerr(str(e))
    finally:
        rospy.signal_shutdown("lane task ended")
