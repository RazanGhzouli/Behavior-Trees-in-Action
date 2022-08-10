#!/usr/bin/env python
import rospy
import sys
import time
from os.path import dirname

sys.path.append((dirname(dirname(__file__))))

import smach
import smach_ros
from bins_vision import BinsDetector
from bins_comm import BinsComms

from  utils.common import *

class Disengage(smach.State):

    def __init__(self, biner):
        smach.State.__init__(self, outcomes=['started', 'aborted'])
        self.biner = biner 
        self.comm = biner.comm

    def execute(self, userdata):
        #Wait for mission planner

        if self.comm.isKilled:
            return 'aborted'

        if self.comm.debug == 2:
            self.comm.isAlone = False
            self.comm.missionBridge("/bins/")
            self.comm.register()
            self.comm.debug = 1 #Reset to prevent multiple registration

        while not self.comm.isStart:
            if self.comm.isKilled: 
                return 'aborted'
            rospy.sleep(rospy.Duration(0.1))

        self.comm.time = time.time()        #Start timer for task
        if self.comm.debug <= 2:
            self.comm.startPID()
        return 'started'


class Find_Bins(smach.State):

    def __init__(self, biner):
        smach.State.__init__(self, outcomes=['done', 'found',  'aborted', 'retry'])
        self.biner = biner 
        self.comm = biner.comm
        self.starting_depth = 0.2

    def execute(self, userdata):

        self.comm.detector = VUtil.findOverallBins
        self.comm.sendMovement(depth=self.starting_depth)

        rospy.logerr("FIND OVERALL BINS")
        rospy.sleep(rospy.Duration(0.5))

        while not self.comm.isKilled:

            if self.comm.outData.data['detected']:
                deltaX = self.comm.outData.data['dxy'][0]
                deltaY = self.comm.outData.data['dxy'][1]
                rospy.logwarn("dx: %.2f dy: %.2f" % (deltaX,deltaY))
                if abs(deltaX) <= 0.05 and abs(deltaY) <= 0.05:
                    #Align parallel to bins
                    currDoa = self.comm.outData.data['angle']
                    self.comm.sendMovement(turn=currDoa)
                    self.comm.sendMovement(turn=90)
                    return 'found'
                self.comm.sendMovement(forward=deltaY*2.0, sidemove=deltaX*3.0, wait=False)

        return 'aborted'

class FindCover(smach.State):

    def __init__(self, biner):
        smach.State.__init__(self, outcomes=['done', 'drop',  'aborted', 'retry'])
        self.biner = biner 
        self.comm = biner.comm
        self.pickup_area = 0.1
        self.pickup_depth = 2.5
        self.rise_depth = 1.2
        self.f_distance = 1.0
        self.fixedDOA = 0
        self.step = [1.0,-2.0]

    def execute(self, userdata):

        self.comm.detector = VUtil.findCover
        rospy.logerr("FIND & LOCATE COVER")
        rospy.sleep(rospy.Duration(0.5))

        '''
        for i in self.step:
            self.comm.sendMovement(forward=i, wait=False, duration=1.0)
            if self.comm.outData.data['detected']:
                break

        '''
        while not self.comm.isKilled:

            if self.comm.outData.data['detected']:
                deltaX = self.comm.outData.data['dxy'][0]
                deltaY = self.comm.outData.data['dxy'][1]
                area = self.comm.outData.data['area']
                angle = self.comm.outData.data['angle']
                rospy.logwarn("dx: %.2f dy: %.2f a: %.2f" % (deltaX,deltaY,area))

                if abs(deltaX) <= 0.05 and abs(deltaY) <= 0.05:

                    rospy.logwarn("Align to bin cover")
                    angle = self.comm.outData.data['angle']
                    self.comm.sendMovement(turn=angle)
                    self.fixedDOA = self.comm.heading

                    while area < self.pickup_area:
                        
                        if self.comm.isKilled:
                            return 'aborted'

                        deltaX = self.comm.outData.data['dxy'][0]
                        deltaY = self.comm.outData.data['dxy'][1]
                        area = self.comm.outData.data['area']
                        rospy.logwarn("dx: %.2f dy: %.2f a: %.2f" % (deltaX,deltaY,area))
                        if abs(deltaX) != 0.2 and abs(deltaY) != 0.2:
                            self.comm.sendMovement(forward=deltaY*1.5, sidemove=deltaX*2.0, depth=self.comm.depth+0.1, turn=self.fixedDOA, 
                                    absolute=True, wait=False, duration=0.6)

                    rospy.logwarn("CENTERING BEFORE DIVING DOWN")

                    while not self.comm.isKilled:

                        if self.comm.outData.data['detected']:
                            deltaX = self.comm.outData.data['dxy'][0]
                            deltaY = self.comm.outData.data['dxy'][1]
                            if abs(deltaX) <= 0.05 and abs(deltaY) <= 0.05:
                                break
                            self.comm.sendMovement(forward=deltaY*1.0, sidemove=deltaX*1.5, depth=self.comm.depth+0.1,wait=False,
                                    duration=0.6)


                    #self.comm.sendMovement(depth=4.0, wait=False, duration=20.0)
                    for i in xrange(20):                        #Diving down and grab
                        self.comm.sendMovement(depth=self.comm.depth+0.2, turn=self.fixedDOA, absolute=True, wait=False, duration=0.8)

                    rospy.logerr("GRABBING")
                    self.comm.grab()

                    while self.comm.depth > self.rise_depth:    #Rising slowly to prevent flipping the bin cover
                        self.comm.sendMovement(depth=self.comm.depth-0.2, turn=self.fixedDOA, absolute=True, wait=False,duration=0.5)

                   
                    self.comm.sendMovement(sidemove=1.0)       #Sidemove to throw away bin cover

                    rospy.logerr("REMOVING COVER")
                    self.comm.drop()

                    self.comm.sendMovement(sidemove=-1.0)
                    self.comm.sendMovement(forward=-0.5)
                    rospy.logerr("DROPPING BALL INTO PRIMARY")

                    while not self.comm.isKilled:

                        if self.comm.outData.data['detected']:
                            deltaX = self.comm.outData.data['dxy'][0]
                            deltaY = self.comm.outData.data['dxy'][1]
                            if abs(deltaX) <= 0.05 and abs(deltaY) <= 0.05:
                                self.comm.dropBall()
                                break
                            self.comm.sendMovement(forward=deltaY*1.5, sidemove=deltaX*2.0, wait=False)

                    return 'drop'

                else:
                    self.comm.sendMovement(forward=deltaY*1.0, sidemove=deltaX*3.0,wait=False,duration=0.6)

        return 'aborted'

class FindSecondary(smach.State):

    def __init__(self, biner):
        smach.State.__init__(self, outcomes=['done', 'drop',  'aborted', 'retry'])
        self.biner = biner 
        self.comm = biner.comm
        self.pickup_area = 0.35
        self.starting_depth = 0.5
        self.dropping_depth = 0.5
        self.target = 3
        self.timeout = 2
        self.step = 1.0
        self.drop = 0

    def execute(self, userdata):
        self.comm.detector = VUtil.findOverallBins
        self.comm.sendMovement(depth=0.2)
        self.comm.sendMovement(forward=-0.5)
        self.comm.sendMovement(sidemove=-0.5)

        rospy.logerr("FIND OVERALL BINS AFTER DROPPING")
        rospy.sleep(rospy.Duration(0.5))


        while not self.comm.isKilled:

            if self.comm.outData.data['detected']:
                deltaX = self.comm.outData.data['dxy'][0]
                deltaY = self.comm.outData.data['dxy'][1]
                rospy.logwarn("dx: %.2f dy: %.2f" % (deltaX,deltaY))
                if abs(deltaX) <= 0.05 and abs(deltaY) <= 0.05:
                    #Align parallel to bins
                    currDoa = self.comm.outData.data['angle']
                    self.comm.sendMovement(turn=currDoa)
                    self.comm.sendMovement(turn=90)
                    break
                self.comm.sendMovement(forward=deltaY*2.0, sidemove=deltaX*3.0, wait=False)

        self.comm.detector = VUtil.findBins3
        rospy.logerr("FIND SECONDARY TARGET")
        rospy.sleep(rospy.Duration(0.5))

        self.comm.sendMovement(depth=0.2)
        while not self.comm.isKilled:

            if self.drop == 2:
                self.comm.taskComplete()
                return 'done'

            data = self.comm.outData.data
            if data['detected']:
                deltaX = data['dxy'][0]
                deltaY = data['dxy'][1]


                if data['pattern'][self.target] != -1:
                    deltaX, deltaY, area = data['pattern'][self.target]
                    rospy.logwarn("dx: %.2f dy: %.2f" % (deltaX,deltaY))

                    if abs(deltaX) <= 0.05 and abs(deltaY) <= 0.05:
                        rospy.logerr("DROP ON SECONDARY TARGET")
                        self.comm.dropBall()
                        self.drop += 1
                        self.target = 2
                    else:
                        self.comm.sendMovement(forward=deltaY*1.0, sidemove=deltaX*3.0,wait=False)

                self.comm.sendMovement(sidemove=self.step, wait=False,duration=1.0)
                self.step *= -1

            else:
                self.comm.sendMovement(sidemove=self.step, wait=False,duration=1.0)
                self.step *= -1

        return 'aborted'

if __name__ == '__main__':
    rospy.init_node('biner')
    mode = rospy.get_param('~mode', 2)
    biner = BinsDetector()
    biner.comm = BinsComms('biner', biner.detect, mode)
    rospy.loginfo("Biner loaded!")

    sm = smach.StateMachine(outcomes=['task_complete', 'aborted'])
    with sm:
        smach.StateMachine.add('DISENGAGE', Disengage(biner),
                               transitions={'started' : 'FIND_SECONDARY',
                                            'aborted' : 'aborted'})

        smach.StateMachine.add('FIND_BINS', Find_Bins(biner),
                               transitions={'found' : 'FIND_SECONDARY',
                                   'aborted' : 'aborted', 'retry':'FIND_BINS',
                                   'done':'task_complete'})

        smach.StateMachine.add('FIND_COVER', FindCover(biner),
                transitions={'drop':'FIND_SECONDARY', 
                                   'aborted' : 'aborted', 'retry':'FIND_BINS',
                                   'done':'task_complete'})


        smach.StateMachine.add('FIND_SECONDARY', FindSecondary(biner),
                transitions={'done':'task_complete', 'drop' : 'DISENGAGE',
                    'aborted' : 'aborted', 'retry':'FIND_BINS'})

    introServer = smach_ros.IntrospectionServer('bins_server',
                                                sm,
                                                '/MISSION/BINS')
    introServer.start()

    try:
        sm.execute()
    except Exception as e:
        rospy.logerr(str(e))
    finally:
        rospy.signal_shutdown("bins task ended")
