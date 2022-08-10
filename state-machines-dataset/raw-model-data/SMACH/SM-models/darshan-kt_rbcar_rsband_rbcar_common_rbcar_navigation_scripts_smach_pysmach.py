'''
Developed by: DARSHAN KT
Objective: Developing the statemachine framework for navigation through multiple target poses.
'''

#!/usr/bin/env python
import rospy
import smach
import time
from smach import State, StateMachine
from smach_ros import SimpleActionState, IntrospectionServer
from geometry_msgs.msg import Twist
from math import  pi
import actionlib
from actionlib import GoalStatus
from geometry_msgs.msg import Pose, Point, Quaternion, Twist
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal, MoveBaseActionFeedback
from tf.transformations import quaternion_from_euler
from collections import OrderedDict

class PowerOnRobot(State):
    def __init__(self):
        State.__init__(self, outcomes=['succeeded'])

    def execute(self, userdata):
	    rospy.loginfo("Powering ON robot...")
	    time.sleep(2)
	    return 'succeeded'
 
class WaitingState(State):
    def __init__(self, waiting_state):
        State.__init__(self, outcomes=['succeeded'])
        self.waiting_state=waiting_state

    def execute(self, userdata):
        if self.waiting_state == 1:
            time.sleep(5)
            return 'succeeded'
        
class main():
    def __init__(self):

        rospy.init_node('ware_house', anonymous=False)
        rospy.on_shutdown(self.shutdown)        
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
    	rospy.loginfo("Waiting for move_base action server...")
    	self.move_base.wait_for_server(rospy.Duration(15))
    	rospy.loginfo("Connected to move_base action server")
        
        
        #create a of angles
        quaternions = list()
        euler_angles = (90.2, 90.3, -89.7, -90, 180)
        for angle in euler_angles:
            q_angle = quaternion_from_euler(0, 0, angle, axes='sxyz')
            q = Quaternion(*q_angle)
            quaternions.append(q)
            print(q)
                
        # self.quaternions.append(0,0, 0.7862, 0.6179)
        # self.quaternions.append(0,0, 0.7775, 0.6288)
        # self.quaternions.append(0,0, -0.441, 0.8974)
        # self.quaternions.append(0,0, -0.6639, 0.7478)
        
    	
     
     # Create a list to hold the waypoint poses
    	self.waypoints = list()
    	self.waypoints.append(Pose(Point(-6.61, -6.23, 0.0), quaternions[0]))
    	self.waypoints.append(Pose(Point(1.24, 12, -0.003), quaternions[1]))
    	self.waypoints.append(Pose(Point(7.52, 16.9, 0.0211), quaternions[2]))
	self.waypoints.append(Pose(Point(7.52, -9.67, 0.0), quaternions[3]))
        self.waypoints.append(Pose(Point(-17.3676, -20.9895, 0.0), quaternions[4]))

        room_locations = (('loading_point1', self.waypoints[0]),
	              ('loading_point2', self.waypoints[1]),
	              ('unloading_point1', self.waypoints[2]),
		          ('unloading_point2', self.waypoints[3]),
                  ('halting_point', self.waypoints[4]))
    
    	# Store the mapping as an ordered dictionary so we can visit the rooms in sequence
        self.room_locations = OrderedDict(room_locations)
        print(self.room_locations)
        nav_states = {}
        
        
        for room in self.room_locations.iterkeys():         
            nav_goal = MoveBaseGoal()
            nav_goal.target_pose.header.frame_id = 'map'
            nav_goal.target_pose.pose = self.room_locations[room]
            move_base_state = SimpleActionState('move_base', MoveBaseAction, goal=nav_goal, result_cb=self.move_base_result_cb, 
                                                exec_timeout=rospy.Duration(23.0),
                                                server_wait_timeout=rospy.Duration(10.0))
            nav_states[room] = move_base_state
            
        sm_warehouse = StateMachine(outcomes=['succeeded','aborted','preempted'])
        with sm_warehouse:
            StateMachine.add('POWER_ON', PowerOnRobot(), transitions={'succeeded':'LOADING_POINT1'})
            StateMachine.add('LOADING_POINT1', nav_states['loading_point1'], transitions={'succeeded':'LOADING_POINT2','aborted':'LOADING_POINT2','preempted':'LOADING_POINT2'})
            StateMachine.add('LOADING_POINT2', nav_states['loading_point2'], transitions={'succeeded':'UNLOADING_POINT1','aborted':'UNLOADING_POINT1','preempted':'UNLOADING_POINT1'})
            StateMachine.add('UNLOADING_POINT1', nav_states['unloading_point1'], transitions={'succeeded':'UNLOADING_POINT2','aborted':'UNLOADING_POINT2','preempted':'UNLOADING_POINT2'})
            # StateMachine.add('WAITING_STATE1', WaitingState(1), transitions={'succeeded':''})
            StateMachine.add('UNLOADING_POINT2', nav_states['unloading_point2'], transitions={'succeeded':'HALTING_POINT','aborted':'HALTING_POINT','preempted':'HALTING_POINT'})
            # StateMachine.add('WAITING_STATE2', WaitingState(1), transitions={'succeeded':''})
            StateMachine.add('HALTING_POINT', nav_states['halting_point'], transitions={'succeeded':'','aborted':'','preempted':''})
            
            intro_server = IntrospectionServer('warehouse', sm_warehouse, '/SM_ROOT')
            intro_server.start()
        
        # Execute the state machine
            sm_outcome = sm_warehouse.execute()      
            intro_server.stop()
            
    def move_base_result_cb(self, userdata, status, result):
        if status == actionlib.GoalStatus.SUCCEEDED:
            # print(status)
            pass


    def shutdown(self):
        rospy.loginfo("Stopping the robot...")
        rospy.sleep(1)

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        rospy.loginfo("Restaurant robot test finished.")


            