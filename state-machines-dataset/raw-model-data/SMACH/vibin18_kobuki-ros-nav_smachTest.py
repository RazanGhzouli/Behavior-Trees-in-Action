#!/usr/bin/env python2

import rospy
import actionlib
import smach
import smach_ros
from smach import State,StateMachine
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import Point

waypoint1 = ['kitchen', (7.660 , 2.905)]
waypoint2 = ['entrance', (-0.577 , 0.151)]

class Waypoint(State):
    def __init__(self, position):
        State.__init__(self, outcomes=['success'])

        # Get an action client
        self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        self.client.wait_for_server()

        # Define the goal
        self.goal = MoveBaseGoal()
        self.goal.target_pose.header.frame_id = 'map'
        self.xGoal = position[0]
        self.yGoal = position[1]
        self.goal.target_pose.pose.position =  Point(self.xGoal,self.yGoal,0)
        self.goal.target_pose.pose.orientation.x = 0.0
        self.goal.target_pose.pose.orientation.y = 0.0
        self.goal.target_pose.pose.orientation.z = 0.0
        self.goal.target_pose.pose.orientation.w = 1.0

    def execute(self, userdata):
        self.client.send_goal(self.goal)
        self.client.wait_for_result()
        return 'success'

if __name__ == '__main__':
    rospy.init_node('patrol')

    # Create a SMACH state machine
    #sm = smach.StateMachine(outcomes=['FAILED', 'SUCESS'])

    patrol = StateMachine(outcomes = ['entrance', 'kitchen'])
    with patrol:
        StateMachine.add('KITCHEN',
            Waypoint(waypoint1[1]),
            transitions={'success': 'entrance'})

        StateMachine.add('ENTRANCE',
            Waypoint(waypoint2[1]),
            transitions={'success': 'kitchen'})
    sis = smach_ros.IntrospectionServer('smach_server', patrol , '/SM_ROOT')
    sis.start()
    patrol.execute()
    sis.stop()
