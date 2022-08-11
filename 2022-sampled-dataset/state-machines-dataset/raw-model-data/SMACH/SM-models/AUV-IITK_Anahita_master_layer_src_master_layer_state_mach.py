#!/usr/bin/env python

import rospy
import smach
import smach_ros
import time
import numpy

from uuv_control_msgs.srv import *
from uuv_control_msgs.msg import Waypoint as WaypointMsg
from master_layer.srv import VerifyObject
from rospy.numpy_msg import numpy_msg
from std_msgs.msg import Time, String
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point
from geometry_msgs.msg import Pose
from std_msgs.msg import Int32
from master_layer.srv import ChangeOdom
from anahita_utils import *

class Transition(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['success','timeout', 'failed'],
                            input_keys=['target_waypoint'])
        self._odom_topic_sub = rospy.Subscriber(
            '/anahita/pose_gt', numpy_msg(Odometry), self.odometry_callback)
        
        
        self._pose = numpy.zeros(3)
        self._threshold = 0.5
        self._timeout = 60 # in seconds
        self._cutoff = 1 # must be comparable to intial distance from the starting point

    def calc_dist(self, current_pose, target_waypoint_msg):
        dist = (current_pose.x - target_waypoint_msg.point.x)*(current_pose.x - target_waypoint_msg.point.x) + \
                (current_pose.y - target_waypoint_msg.point.y)*(current_pose.y - target_waypoint_msg.point.y) + \
                (current_pose.z - target_waypoint_msg.point.z)*(current_pose.z - target_waypoint_msg.point.z)
        return dist

    def odometry_callback(self, msg):
        self._pose = numpy.array([msg.pose.pose.position.x,
                                msg.pose.pose.position.y,
                                msg.pose.pose.position.z])
    
    def execute(self, userdata):
        target_waypoint_msg = WaypointMsg()
        target_waypoint_msg = userdata.target_waypoint.to_message()
        
        print 'waiting for go to waypoint server'
        rospy.wait_for_service('anahita/go_to')

        go_to = rospy.ServiceProxy('anahita/go_to', GoTo)

        start_time = Time()
        start_time.data.secs = rospy.get_rostime().to_sec()
        start_time.data.nsecs = rospy.get_rostime().to_nsec()
        
        interpolator = String()
        interpolator.data = 'cubic_interpolator'
        print 'adding waypoints....'
        resp = init_waypoint_set(max_forward_speed = 0.5, 
                                interpolator = interpolator,
                                waypoint = target_waypoint_msg)

        then = rospy.get_time()

        while not rospy.is_shutdown():
            now = rospy.get_time()
            dt = now - then
            dist = calc_dist(self._pose, target_waypoint_msg)
            
            if dist < self._threshold:
                return 'success'

            if dt > self._timeout:
                return 'timeout'

            if dist > self._cutoff:
                return 'failed'

class TaskBaseClass(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=['random_outcome1', 'random_outcome2'],
                            input_keys=['field1', 'field2', 'field3'],
                            output_keys=['field1', 'field2', 'field2'])

        self._odom_topic_sub = rospy.Subscriber('/anahita/pose_gt', Odometry, self.odometry_callback)
        self._conventional_detection_pub = rospy.Subscriber('/anahita/conventional_detection', Int32, self.conventional_detector_cb)
        self._pose_cmd_pub = rospy.Publisher('/anahita/cmd_pose', Pose, queue_size=10)
        self._conventional_prob = 0
        
        try:
            self._change_odom = rospy.ServiceProxy('odom_source', ChangeOdom)
            
        except rospy.ServiceException, e:
            print "Service call failed: %s"
    
    def has_reached (self, pos, threshold):
        while (not status or rospy.is_shutdown()):
            return False
        while (calc_dist(pos, self._pose) > threshold or rospy.is_shutdown()):
            return False
        return True

    def odometry_callback(self, msg):
        rospy.loginfo("Current pose: " + str(msg))
        self._pose = msg.pose.pose.position
        self._orientation = msg.pose.pose.orientation
        global status
        status = True 

    
        
    def load_params(self):
        # start point for the task
        pass

    def start_stereo(self):
        # after the verification of the object start visual odometry
        pass

    def execute(self):
        pass

    def object_detector(self):  
        # to start object recognition as soon the bot enters
        # that task and confirm it is the same object
        # a service to ask vision layer if it is the same object
        # vision layer will recognize for a particular period of time
        # and verify the object

        print 'waiting for object recognition server'
        rospy.wait_for_service('anahita/object_recognition')

        verify_object = rospy.ServiceProxy('anahita/object_recognition', VerifyObject)
        resp = verify_object(object='')

        if resp:
            return True
        else:
            return False
    
    def conventional_detector_cb(self, msg):
        self._conventional_prob = msg.data
        

class MoveToXYZ(TaskBaseClass):
    
    def __init__(self):
        TaskBaseClass.__init__(self)
        print("Creating an approachXYZ task")
        smach.State.__init__(self, outcomes=['found_visually', 'cannot_see', 'lost'],
                            input_keys=['task_found', 'field2', 'field3'],
                            output_keys=['field1', 'field2', 'field2'])
        change_odom_response = self._change_odom(odom="dvl")
        self.then_ = rospy.get_time()
        self.timeout_ = 50
        self.target_pose_ = Pose()
        self.start_moving()
        self.present_status()
    
    def start_moving(self):
        fill_pose_data(self.target_pose_, 10, 10, 1.5, 0, 0, 0, 1)
        self._pose_cmd_pub.publish(self.target_pose_)
        rospy.loginfo("We are now moving towards the target pose" + str(self.target_pose_))
    
    def present_status(self):
        rospy.loginfo("Now, I'll check whatever is happening")
        
        while True:
            rospy.loginfo("I am seraching, prob: " + str(self._conventional_prob))
            if self._conventional_prob > .80:
                rospy.loginfo("changing to visual odom")
                change_odom_response = self._change_odom(odom="vision")
                return 'found_visually'
        
            if self.has_reached(self.target_pose_.position, 3) is True:
                rospy.loginfo("reached the position")
                return 'cannot_see'
            
            now = rospy.get_time()
            dt = now - self.then_
            if dt > self.timeout_:
                rospy.loginfo("I've lost")
                return 'lost'


class BouyTask(TaskBaseClass):
    def __init__(self):
        TaskBaseClass.__init__(self)

    def hit_buoy(self):
        # a service call to goto for hitting the buoy
        pass

    def get_back(self):
        # a goto request to get back to its initial point
        pass

    def execute(self):
        # can make a sub state machine to define the before hitting and after 
        # hitting in separate states
        pass

# if every task state execute will contains different set of member functions to 
# complete the task like in buoy it will be hit_buoy() and in gate it will be just
# move forward
class GateTask(TaskBaseClass):
    def __init__(self):
        TaskBaseClass.__init__(self)

    def wait_for_crossing(self):
        # to wait for the lower part of a pipe to be identified by the vision layer
        # to send a request to the vision layer to do it with a timeout
        pass

    def move_forward(self):
        # cross the gate
        pass

    def execute(self):
        pass

class TorpedoTask(TaskBaseClass):
    def __init__(self):
        TaskBaseClass.__init__(self)

    def take_position(self):
        # take position to fire the torpedo
        # by making a req to the goto server
        pass

    def fire_torpedo(self):
        pass

    def execute(self):
        pass

class MarkerDropperTask(TaskBaseClass):
    def __init__(self):
        TaskBaseClass.__init__(self)

    def align(self):
        pass

    def execute(self):
        pass

class OctagonTask(TaskBaseClass):
    def __init__(self):
        TaskBaseClass.__init__(self)

    def localise(self):
        pass

    def execute(self):
        pass

class LineTask(TaskBaseClass):
    def __init__(self):
        TaskBaseClass.__init__(self)

    def align(self):
        # to align with the line
        pass
    
    def move_forward(self):
        # after aligning to the line move forward
        pass

    def execute(self):
        pass

# there are two kinds of findings that need to be dealt with
# 1. one to find the object with the bottom camera
# 2. and one with the front camera

class FindBottomTarget(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['outcome2'])

    def execute(self, userdata):
        # request to move in a circle or helix to the local planner
        pass

    def explore(self):
        # move around to find a target
        pass

class FindFrontTarget(smach.State):

    def __init__(self):
        rospy.loginfo("I am not able to see things, let's turn around and find something")
        smach.State.__init__(self, outcomes=['found_visually', 'lost'])
    
        global status
        status = True
        self._odom_topic_sub = rospy.Subscriber('/anahita/pose_gt', Odometry, self.odometry_callback)
        self._conventional_detection_pub = rospy.Subscriber('/anahita/conventional_detection', Int32, self.conventional_detector_cb)
        self._ml_detection_pub = rospy.Subscriber('/anahita/ml', Int32, self.ml_cb)
        self._pose_cmd_pub = rospy.Publisher('/anahita/cmd_pose', Pose, queue_size=10)
        
        self._conventional_prob = 0
        self._ml_prob = 0
        self._then = rospy.get_time()
        self._timeout = 120
        self._step_timeout = 5
        self._target_pose = Pose()
        self._pos = self._target_pose.position
        self._orientation = self._target_pose.orientation
        self._current_pose = Pose()
        self.execute()
        

        try:
            self._change_odom = rospy.ServiceProxy('odom_source', ChangeOdom)   
        except rospy.ServiceException, e:
            print "Service call failed: %s"

        change_odom_response = self._change_odom(odom="dvl")
    
    def conventional_detector_cb(self, msg):
        self._conventional_prob = msg.data
    def ml_cb(self, msg):
        self._ml_prob = msg.data

    def odometry_callback(self, msg):
        self._current_pose = msg.pose.pose
        self._pos = msg.pose.pose.position
        self._orientation = msg.pose.pose.orientation
        _curr_roll, _curr_pitch, _curr_yaw = quaternion_to_eulerRPY(self._orientation)
        global status
        status = True 
    
    def has_reached_with_yaw(self, target_pose, curr_pose, pos_threshold, yaw_threshold):
        while (not status or rospy.is_shutdown()):
            return False
        while (calc_dist(target_pose.position, curr_pose.position) > pos_threshold or rospy.is_shutdown()):
            return False
        _curr_roll, _curr_pitch, _curr_yaw = quaternion_to_eulerRPY(curr_pose.orientation)
        _target_roll, _target_pitch, _target_yaw = quaternion_to_eulerRPY(target_pose.orientation)
        while (abs(_curr_yaw - _target_yaw) > yaw_threshold):
            return False
        return True

    def execute(self):
        # move the bot to the pose according to the odom frame of ref 
        # and then rotate the bot to search object

        #we'll use the initial yaw reference over here
        fill_pose_data(self._target_pose, self._pos.x, self._pos.y, self._pos.z, 0, 0, 0, 1)
        self._pose_cmd_pub.publish(self._target_pose)
        while self.has_reached_with_yaw(self._target_pose, self._current_pose, 1, 10) is False:
            rospy.loginfo("Still reaching the initial start position")
               
        _now = rospy.get_time()
        dt = _now - self._then
        
        _target_pos = self._pos
        _start_roll, _start_pitch, _start_yaw = quaternion_to_eulerRPY(self._current_pose.orientation)
        _target_roll = 0
        _target_pitch = 0
        _target_yaw = TO_DEGREE(_start_yaw)
        rospy.loginfo("The yaw before starting out is: " + str(_start_yaw))
        
        while dt < self._timeout:
            rospy.loginfo("Still trying to search my boi")

            _target_yaw += 30
            if(_target_yaw>180):
                _target_yaw -= 360
            rospy.loginfo('The target yaw is: ' + str(_target_yaw))
            target_quaternion = eulerRPY_to_quaternion(_target_roll, _target_pitch, TO_RADIAN(_target_yaw))
            
            fill_pose_data_pq(self._target_pose, self._pos, target_quaternion)
            self._pose_cmd_pub.publish(self._target_pose)
            rospy.sleep(self._step_timeout)

            if(self._conventional_prob > 0.8):
                rospy.loginfo("Conventionally mila hai kuch chod")  
                return 'found_visually'

            if(self._ml_prob > 0.8):
                rospy.loginfo("ML se milgya, nice bro")
                return 'found_visually'
            
        return 'lost'

    def explore(self):
        pass
        # move around to find a target

# there are two kinds of scenarios for finding
# 1. when the bot is working properly but is not able to find the
#    object at the current position so it goes into `find target state`
# 2. something very bad happens to the like the thruster behaving weirdly 
#    and dragging to the direction where it should not go, in that situation 
#    it becomes necessary for the reset all the things and plan for itself 
#    according to the task it has done and last pose that it remebers and 
#    use path planning algorithms to generate waypoints for the trajectory generation

class RescueMode(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['some_outcome'])

    def execute(self):
        # monitor the path tracing
        pass

    def localise(self):
        # locate where is it now
        # can make a special service for this
        pass

    def next_task(self):
        # gives the next task to approach
        pass

    def path_to_new_target(self):
        # use a service to get the path from a path algorithm
        pass

    def trace_path(self):
        # make a request to the init_waypoint_server for trajectory generation
        pass

class IdentifyTarget(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=[''], input_keys=['target'])
        rospy.loginfo("Identifying the target")
        


class TooFar(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=[''],
                            input_keys=['target'])

    def execute(self):
        pass
    
    def stop(self):
        # if the bot is going out of the way of any target
        # then stop it
        pass

    def restore(self):
        # restore to a position from where it can still do the task
        pass

class StationKeeping(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['success'])

    def execute(self):
        # just maintain the current pose
        pass

if __name__ == '__main__':
    rospy.init_node('state_machine')

    # Create a SMACH state machine
    sm = smach.StateMachine(outcomes=['outcome4'])

    # Open the container
    with sm:
        # Add states to the container
        smach.StateMachine.add('MovingToXYZ', MoveToXYZ(), 
                               transitions={'found_visually':'IdentifyTarget', 'cannot_see':'FindFrontTarget', 'lost':'MovingToXYZ'})
                                   
        smach.StateMachine.add('FindFrontTarget', FindFrontTarget(), transitions = {'found_visually':'IdentifyTarget', 'lost':'MovingToXYZ'})
        smach.StateMachine.add('IdentifyTarget', IdentifyTarget())
    
    sis = smach_ros.IntrospectionServer('smach_introspect', sm, '/SM_ROOT')
    sis.start()

    outcome = sm.execute()

    rospy.spin()
    sis.stop()

    # Execute SMACH plan
    

