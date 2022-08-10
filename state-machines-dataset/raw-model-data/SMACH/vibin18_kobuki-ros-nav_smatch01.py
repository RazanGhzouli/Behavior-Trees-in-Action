#!/usr/bin/env python2

import rospy
import actionlib
import smach
import smach_ros
from smach import State,StateMachine
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import Point


class Waypoint(State):
    def __init__(self, position):
        State.__init__(self, outcomes=['success','failed'])

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
        self.client.wait_for_result(rospy.Duration(360))
        if(self.client.get_state() ==  actionlib.GoalStatus.SUCCEEDED):
#                rospy.loginfo("You have reached the destination")
                return 'success'

        else:
#                rospy.loginfo("The robot failed to reach the destination")
                return 'failed'



if __name__ == '__main__':

    rospy.init_node('stateMachine1')
    stateMachine1 = smach.StateMachine(outcomes=['FAILED'])

    with stateMachine1:
        StateMachine.add('KITCHEN',
            Waypoint([4.47968006134 ,1.00167346001]),
            transitions={'success': 'ENTRANCE', 'failed' : 'KITCHEN' })

        StateMachine.add('ENTRANCE',
            Waypoint([-0.577 , 0.151]),
            transitions={'success': 'KITCHEN', 'failed' : 'ENTRANCE' })

    sis = smach_ros.IntrospectionServer('smach_server', stateMachine1 , '/SM_ROOT')
    sis.start()
    stateMachine1.execute()
    sis.stop()
