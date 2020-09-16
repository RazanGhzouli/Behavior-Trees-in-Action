#! /usr/bin/env python

# standard ros server things
import rospy, actionlib, py_trees
import std_msgs.msg as std_msgs

import actionlib
import dynamic_reconfigure.server
import rospy
import py_trees_ros
#from sam_march.msg import GenericStringAction

from py_trees_ros.mock.action_server import ActionServer
from sam_march.msg import GenericStringAction
from sam_msgs.msg import PercentStamped
from uuv_gazebo_ros_plugins_msgs.msg import FloatStamped
from std_msgs.msg import Bool


class Emergency(ActionServer):

    def __init__(self):
        ActionServer.__init__(self, '/sam_emergency', GenericStringAction, self.worker)
        self.publisher = rospy.Publisher('/sam_auv_1/thrusters/0/input',
                                         FloatStamped,
                                         queue_size = 100)

        self.controller_stopper = rospy.Publisher('/VBS_depth/pid_enable',
                                                  Bool,
                                                  queue_size = 100)
    def worker(self):
        print("")

    def execute(self, goal):
        # We override
        """
        Check for pre-emption, but otherwise just spin around gradually incrementing
        a hypothetical 'percent' done.

        Args:
            goal (:obj:`any`): goal of type specified by the action_type in the constructor.
        """
        #if self.goal_received_callback:
        #    self.goal_received_callback(goal)
        # goal.target_pose = don't care
        frequency = 3.0  # hz
        increment = 100 / (frequency * self.parameters.duration)
        self.percent_completed = 0
        rate = rospy.Rate(frequency)  # hz
        rospy.loginfo("{title}: received a goal".format(title=self.title))

        # if we just received a goal, we erase any previous pre-emption
        self.action_server.preempt_request = False
        while True:
            if rospy.is_shutdown() or self.action_server.is_preempt_requested():
                rospy.loginfo("{title}: goal preempted".format(title=self.title))
                self.action_server.set_preempted(self.action.action_result.result, "goal was preempted")
                success = False
                break
            if self.percent_completed >= 100:
                rospy.loginfo("{title}: feedback 100%".format(title=self.title))
                success = True
                break
            else:
                #rospy.loginfo("{title}: YOLOY emergency feedback {percent:.2f}%".format(title=self.title, percent=self.percent_completed))
                #self.percent_completed += increment
                #self.worker()
                fs = PercentStamped()
                h = Header()
                fs.header = h
                fs.data = 0
                self.publisher.publish(fs)
                self.controller_stopper.publish(False)
            rate.sleep()
        if success:
            rospy.loginfo("{title}: goal success".format(title=self.title))
            self.action_server.set_succeeded(self.action.action_result.result, "goal reached")





if __name__ == "__main__":

    # emergency action server
    rospy.init_node('emergency_action')
    act = Emergency()
    act.start()
    rospy.spin()
