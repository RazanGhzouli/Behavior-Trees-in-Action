#!/usr/bin/env python
import rospy
from smach import StateMachine
from smach_ros import SimpleActionState
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal

waypoints = [
['one', (-3.37, 4.98), (0.0, 0.0, 0.07, 1.0)],
['two', (-4.27, 18.6), (0.0, 0.0, -0.984047240305, 0.177907360295)]
]

if __name__ == '__main__':
    rospy.init_node('patrol')
    patrol = StateMachine(['succeeded','aborted','preempted'])
    with patrol:
        for i,w in enumerate(waypoints):
            goal_pose = MoveBaseGoal()
            goal_pose.target_pose.header.frame_id = 'map'
            goal_pose.target_pose.pose.position.x = w[1][0]
            goal_pose.target_pose.pose.position.y = w[1][1]
            goal_pose.target_pose.pose.position.z = 0.0
            goal_pose.target_pose.pose.orientation.x = w[2][0]
            goal_pose.target_pose.pose.orientation.y = w[2][1]
            goal_pose.target_pose.pose.orientation.z = w[2][2]
            goal_pose.target_pose.pose.orientation.w = w[2][3]
            
            StateMachine.add(w[0],
                            SimpleActionState('move_base',
                            MoveBaseAction,
                            goal=goal_pose, exec_timeout=rospy.Duration(15.0),
                                                    server_wait_timeout=rospy.Duration(10.0)),
                            transitions={'succeeded':waypoints[(i + 1) % \
                            len(waypoints)][0]})


    patrol.execute()