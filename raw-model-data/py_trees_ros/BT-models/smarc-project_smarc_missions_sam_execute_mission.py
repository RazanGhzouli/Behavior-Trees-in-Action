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
from std_msgs.msg import Float64



class Execute_Mission(ActionServer):

    def __init__(self):
        ActionServer.__init__(
            self,
            '/execute_mission',
            GenericStringAction,
            self.worker
        )

        self.pitch_publisher = rospy.Publisher('/pitch_setpoint',
                                                Float64,
                                                queue_size = 100)

        self.depth_publisher = rospy.Publisher('/depth_setpoint',
                                                Float64,
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

        goal = eval(goal.bt_action_goal)
        rospy.loginfo("{title}: received a goal:{goal}".format(title=self.title, goal=str(goal)))

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
                #rospy.loginfo("{title}: mission execution feedback {percent:.2f}%".format(title=self.title, percent=self.percent_completed))
                #self.percent_completed += increment
                #self.worker()

                if goal is None:
                    return False

                pitch, depth = goal
                self.pitch_publisher.publish(pitch)
                self.depth_publisher.publish(depth)





            rate.sleep()
        if success:
            rospy.loginfo("{title}: goal success".format(title=self.title))
            self.action_server.set_succeeded(self.action.action_result.result, "goal reached")



if __name__ == "__main__":

    # emergency action server
    rospy.init_node('execute_mission')
    act = Execute_Mission()
    act.start()
    rospy.spin()
