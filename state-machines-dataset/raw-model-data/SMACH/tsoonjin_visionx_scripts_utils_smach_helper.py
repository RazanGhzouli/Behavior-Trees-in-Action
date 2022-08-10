#!/usr/bin/env python
"""Contains classes and reuseable functions to setup a taskrunner using SMACH state 
machine library
"""
import abc
import time
import signal

import rospy
import smach
import smach_ros

'''Generic states'''

class GenericState(smach.State):
    def __init__(self, name, transitions):
        self.name = name
        self.transitions = transitions
        self.start_time = None
        smach.State.__init__(self, outcomes=transitions.keys())

    def changeState(self, outcome):
        elapse = (time.time() - self.start_time)/60.0   #time taken in state
        return outcome

class Static(smach.State):
    """See-only mode where the vehicle is moved around by diver or manually to 
    simulate specific scenario to test robustness of vision algorithm
    """
    def __init__(self, outcomes_list):
        self.name = 'JUST_OBSERVING'
        self.transitions = {'completed':'done'}
        smach.State.__init__(self, outcomes=['completed'])
    
    def execute(self, userdata):
        while not userdata.completed:
            rospy.sleep(rospy.Duration(5.0))
        return 'completed'

'''Decorators'''
def start_time(func):
    def wrapper(self, *args, **kwargs):
        self.start_time = time.time()
        return func(*args, **kwargs)
    return wrapper

'''SMACH'''

def _initIntroServer(server_name, sm, path):
    """Initiazes introspection server"""
    introServer = smach_ros.IntrospectionServer(server_name, sm, path)
    introServer.start()

def _initSMACH(self, comm, states_list):
    """Initializes State Machine container and add states
    Args:
        states: list of states that will be added 
        outcomes: list of possible outcomes 
    Returns:
        sm: Smach state machine instance
    """
    outcomes_list = ['done', 'aborted']
    sm = smach.StateMachine(outcomes=outcomes_list)
    sm.userdata.comm = comm
    #Adding States from list 
    with sm:
        for state in states_list:
            smach.StateMachine.add(state.name, state, transitions=state.transitions)
    return sm

def _executeTask(self, comm, states_list):
    """Initializing ROS node and start state machine
    Args:
        comm: Task specific communication module
    """
    sm = initSMACH(states_list)
    sm.userdata = comm      #set userdata to comm object to share data between states
    initIntroServer(comm.name, sm, '/MISSION/{}'.format(comm.name.upper()))
    try:
        sm.execute()
    except Exception as e:
        rospy.logerr(str(e))
    finally:
        rospy.signal_shutdown('{} ended successfully'.format(comm.name))
    
'''ROS related'''

def startTask(self, comm, states_list):
    #Handle Ctrl+C and kill
    signal.signal(signal.SIGINT, comm.handleInterupt)
    signal.signal(signal.SIGTERM, comm.handleInterupt)
    #Initialize ROS node
    rospy.init_node(comm.name)
    _executeTask(comm, states_list)

def isDormant(self, comm):
    return not comm.alone and not comm.activated

def setup(name, detector):
    """Setup configuration and communication of ROS node
    Args:
        name: name of ROS node
    Returns:
        comm: object that handles communication with ROS
    """
    config = BaseConfig(name, detector)
    rospy.init_node(config.name)
    comm = BaseComm(config)
    return comm

'''Movement code'''

def centerToObject(comm, mult=(1.5, 2.0), limit=0.05):
    """Center to object of interest after detection
    Args:
        coeff: multiplier to forward and sidemove goals
        limit: error between centroid of object and center before terminating
    """
    while True:
        if comm.output.detected:
            if(abs(comm.output.dx) <= limit and abs(comm.output.dy) <= limit):
                break
            else:
                comm.move(f=mult[1]*comm.output.dy, sm=mult[0]*comm.output.dx, duration=0.5)

def searchForward(comm, limit=2):
    """Move forward slowly while detecting object of interest
    Args:
        limit: number of detection required before termination to remove false positive
    """
    count = 0
    while True:
        if count is limit:                     #stop searching after fulfilling limit
            break
        elif comm.output.detected:
            count += 1
        else:
            comm.move(f=1.0, duration=0.5)     #search forward slowly

