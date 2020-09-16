#!/usr/bin/env python

import py_trees as pt
import py_trees_ros as ptr
import rospy
from behaviours_student import *
from reactive_sequence import RSequence
from std_srvs.srv import Empty, SetBool, SetBoolRequest
from actionlib import SimpleActionClient
from play_motion_msgs.msg import PlayMotionAction, PlayMotionGoal
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped


class pickcube(pt.behaviour.Behaviour):

    def __init__(self):
        rospy.loginfo("Initialising move head behaviour.")
        pick_cube_srv_name = rospy.get_param(rospy.get_name() + '/pick_srv')
        self.pick_cube_srv = rospy.ServiceProxy(pick_cube_srv_name, SetBool)
        rospy.wait_for_service(pick_cube_srv_name, timeout=30)
		# execution checker
        self.tried = False
        self.done = False
        # become a behaviour
        super(pickcube, self).__init__("pickcube")

    def update(self):
        # success if done
        if self.done:
            return pt.common.Status.SUCCESS

		# try if not tried
        elif not self.tried:
            # command
            self.pick_cube_req = self.pick_cube_srv(True)

            self.tried = True

            # tell the tree you're running
            return pt.common.Status.RUNNING

		# if succesful
        elif self.pick_cube_req.success:
            self.done = True
            return pt.common.Status.SUCCESS

		# if failed
        elif not self.pick_cube_req.success:
            return pt.common.Status.FAILURE

		# if still trying
        else:
            return pt.common.Status.RUNNING


class placecube(pt.behaviour.Behaviour):

    def __init__(self):
        rospy.loginfo("Initialising move head behaviour.")
        place_cube_srv_name = rospy.get_param(rospy.get_name() + '/place_srv')
        self.place_cube_srv = rospy.ServiceProxy(place_cube_srv_name, SetBool)
        rospy.wait_for_service(place_cube_srv_name, timeout=30)
        # execution checker
        self.tried = False
        self.done = False
        # become a behaviour
        super(placecube, self).__init__("placecube")

    def update(self):
        # success if done
        if self.done:
            return pt.common.Status.SUCCESS

		# try if not tried
        elif not self.tried:
            # command
            self.place_cube_req = self.place_cube_srv(True)

            self.tried = True
            return pt.common.Status.RUNNING

		# if succesful
        elif self.place_cube_req.success:
            self.done = True
            return pt.common.Status.SUCCESS

		# if failed
        elif not self.place_cube_req.success:
            return pt.common.Status.FAILURE

		# if still trying
        else:
            return pt.common.Status.RUNNING


class is_cube_placed(pt.behaviour.Behaviour):

    def __init__(self):
        self.aruco_pose_top = rospy.get_param(
            rospy.get_name() + '/aruco_pose_topic')
        
        def aruco_callback(_):
            self.aruco_pose_rcv = True
                    
        self.aruco_pose_subs = rospy.Subscriber(
            self.aruco_pose_top, PoseStamped, aruco_callback)
        
        super(is_cube_placed, self).__init__("is_cube_placed")
   
    def update(self):
        self.aruco_pose_rcv = False
        
        rospy.sleep(5)
        
        if self.aruco_pose_rcv == True:
            rospy.loginfo("Cube placed return success")
            exit()
            return pt.common.Status.SUCCESS
        else:
            rospy.logerr("Cube missing return fail")
            return pt.common.Status.FAILURE


def build_change_table(name):
    
    turn_around = pt.composites.Selector(
		name="Turn around",
		children=[counter(58, "Turned around?"), go("Turn", 0, -0.5)]
	)

    go_straight = pt.composites.Selector(
		name="Walk",
		children=[counter(20, "At table?"), go("Walk", 0.4, 0)]
	)
    
    timeout = pt.decorators.Timeout(
			name="Timeout",
			child=pt.behaviours.Success(name="Have a Beer!"),
			duration=100.0
	)

    return RSequence(name=name, children=[turn_around, go_straight, timeout])


class BehaviourTree(ptr.trees.BehaviourTree):

    def __init__(self):

        rospy.loginfo("Initialising behaviour tree")
        
        is_placed = pt.composites.Selector(
            name="twist",
            children=[counter(2, "Is Placed?"), is_cube_placed()]
        )
        
        confirm_placed_cube = pt.composites.Chooser(
            name="Confirm cube is on table",
            children=[is_placed, build_change_table('Go back')])
        
        place = pt.composites.Selector(
            name="twist",
            children=[counter(60, "Placed?"), placecube()])
        
        pick = pt.composites.Selector(
            name="twist",
            children=[counter(60, "Picked?"), pickcube()])
        
        tree = RSequence(name="Main sequence", children=[
            tuckarm(),
            movehead("down"),
            pick, 
            build_change_table('Go to other table'),
            place,
            confirm_placed_cube,
		])

        super(BehaviourTree, self).__init__(tree)

        # execute BT
        rospy.sleep(1)
        self.setup(timeout=10000)
        while not rospy.is_shutdown():
            self.tick_tock(1)


if __name__ == "__main__":

    rospy.init_node('main_state_machine')
    try:
        BehaviourTree()
    except rospy.ROSInterruptException:
        pass

    rospy.spin()
