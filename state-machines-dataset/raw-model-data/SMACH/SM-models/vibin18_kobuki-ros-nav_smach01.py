#!/usr/bin/env python2

bedroom = (-3.928, 1.248)
entrance = (-1.118, 0.183)
tvroom = (7.734, 1.855)

import rospy
import actionlib
import smach
import smach_ros
from smach import State,StateMachine
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import Point
import roslib; roslib.load_manifest('sound_play')
from sound_play.msg import SoundRequest, SoundRequestAction, SoundRequestGoal

class Waypoint(State):
    def __init__(self, position):
        State.__init__(self, outcomes=['success','failed'])

        # Get an action client
        self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)


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
        self.client.wait_for_server()
        self.client.send_goal(self.goal)
        self.client.wait_for_result(rospy.Duration(360))
        if(self.client.get_state() ==  actionlib.GoalStatus.SUCCEEDED):
#                rospy.loginfo("You have reached the destination")
                return 'success'

        else:
#                rospy.loginfo("The robot failed to reach the destination")
                return 'failed'

class speak(State):
    def __init__(self, matter):
        State.__init__(self, outcomes=['success', 'failed'])
        self.client = actionlib.SimpleActionClient('sound_play', SoundRequestAction)
        self.client.wait_for_server()
        self.goal = SoundRequestGoal()
        self.matter = matter

    def execute(self, userdata):
        rospy.loginfo("Say")
        self.goal.sound_request.sound = SoundRequest.SAY
        self.goal.sound_request.command = SoundRequest.PLAY_ONCE
        self.goal.sound_request.arg = self.matter
        self.goal.sound_request.volume = 1.0

        self.client.send_goal(self.goal)
        if(self.client.get_state() ==  actionlib.GoalStatus.SUCCEEDED):
            rospy.loginfo("End Say Succeded")
            return 'success'
        else:
            while (self.client.get_state() !=  actionlib.GoalStatus.SUCCEEDED):
                rospy.sleep(2.)
                if(self.client.get_state()==  actionlib.GoalStatus.PENDING):
                    rospy.sleep(2.)
                    rospy.loginfo("Speaking is pending")
                elif(self.client.get_state() == actionlib.GoalStatus.SUCCEEDED):
                    rospy.loginfo("End Say Success")
                    return 'success'
                elif(self.client.get_state() == actionlib.GoalStatus.ABORTED):
                    rospy.loginfo("End Say Failed")
                    return 'failed'
                else:
                    rospy.sleep(2.)
            else:
                return 'success'





if __name__ == '__main__':

    rospy.init_node('stateMachine1')
    stateMachine1 = smach.StateMachine(outcomes=['FAILED'])
    kitchenMatter = " I have reached kitchen and i am heading to entrance room."
    entranceMatter = " I have reached the entrance room. now i am heading to kitchen."
    henna = " nna-nun o-ru Kobuki aay-ru-ne-nngili, taada."

    with stateMachine1:
        StateMachine.add('KITCHEN',
            Waypoint([6.813, 1.325]),
            transitions={'success': 'SPEAK_KITCHEN', 'failed' : 'ENTRANCE' })

        StateMachine.add('SPEAK_KITCHEN',
            speak(kitchenMatter),
            transitions={'success': 'ENTRANCE', 'failed' : 'FAILED' })

        StateMachine.add('ENTRANCE',
            Waypoint([-1.118, 0.183]),
            transitions={'success': 'SPEAK_ENTRANCE', 'failed' : 'KITCHEN' })

        StateMachine.add('SPEAK_ENTRANCE',
            speak(entranceMatter),
            transitions={'success': 'KITCHEN', 'failed' : 'FAILED' })

    sis = smach_ros.IntrospectionServer('smach_server', stateMachine1 , '/SM_ROOT')
    sis.start()
    stateMachine1.execute()
    sis.stop()
