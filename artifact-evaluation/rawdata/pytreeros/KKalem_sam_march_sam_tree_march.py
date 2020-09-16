#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Author: Ozer Ozkahraman (ozkahramanozer@gmail.com)
# 1 Mar 2019


from __future__ import print_function

import rospy, time
import actionlib

import functools, sys, time

from std_msgs.msg import Empty, Bool, Float64
from sam_march.msg import GenericStringAction, GenericStringGoal

import py_trees as pt
import py_trees_ros as ptr

from reactive_seq import ReactiveSeq
from sf_timer import SF_Timer

import sam_behaviours
from sam_emergency import Emergency
from sam_execute_mission import Execute_Mission

import random

# make these HUGE if you dont care about these checks
PITCH_THRE = 10000000
DEPTH_THRE = 0.1

# pitch depth
MISSION_SETPOINTS = [(0,30), (0,32), (0.2, 32), (-0.2, 32), (0,30), (0,0)]
IDLES_MADE = 0


def make_idle():
    # a node that just keeps running once the tree is done
    global IDLES_MADE
    IDLES_MADE += 1
    return pt.behaviours.Running(name='Idle '+str(IDLES_MADE))

def check_pitch_fn(p1,p2):
    diff = abs(p1-p2)
    if diff < PITCH_THRE:
        return True
    return False

def check_depth_fn(p1,p2):
    diff = abs(p1-p2)
    if diff < DEPTH_THRE:
        return True
    return False

def make_follow_points_subtree(points):
    seq = pt.composites.Sequence(name="Mission sequence")

    for pt_ix, point in enumerate(points):
        pitch, depth = point



        check_pitch = pt.blackboard.CheckBlackboardVariable(name="Pitch?",
                                                            variable_name='pitch',
                                                            expected_value=pitch,
                                                            comparison_operator=check_pitch_fn)

        check_depth = pt.blackboard.CheckBlackboardVariable(name="Depth?",
                                                            variable_name='depth',
                                                            expected_value=depth,
                                                            comparison_operator=check_depth_fn)


        target_check = pt.composites.Parallel(name="At target?")
        target_check.add_children([check_pitch, check_depth])

        set_point_done = pt.blackboard.SetBlackboardVariable(name="Set point"+str(pt_ix)+" done",
                                                             variable_name=str(pt_ix)+"_done",
                                                             variable_value=True)

        point_done_seq = ReactiveSeq(name="GOTO then set flag")
        point_done_seq.add_children([target_check, set_point_done])


        goto_pnt_msg = GenericStringGoal()
        goto_pnt_msg.bt_action_goal = str(point)
        goto_pnt_action = ptr.actions.ActionClient(name='goto_'+str(point),
                                                   action_spec=GenericStringAction,
                                                   action_goal=goto_pnt_msg,
                                                   action_namespace='/execute_mission')




        check_timeout_flag = pt.blackboard.CheckBlackboardVariable(name="Check timeout flag",
                                                                   variable_name=str(pt_ix)+'_timeout_triggered',
                                                                   expected_value=True)

        timeout = SF_Timer(name="Timeout", duration=60)
        set_timeout_flag = pt.blackboard.SetBlackboardVariable(name="Set timeout flag",
                                                               variable_name=str(pt_ix)+'_timeout_triggered',
                                                               variable_value=True)

        check_timeout = ReactiveSeq(name='Check timeout')
        check_timeout.add_children([timeout, set_timeout_flag])

        check_point_done_flag = pt.blackboard.CheckBlackboardVariable(name="Check point done flag",
                                                                      variable_name=str(pt_ix)+'_done',
                                                                      expected_value=True)


        at_target_fb = pt.composites.Selector(name="Not at"+str(point)+"?")
        at_target_fb.add_children([check_timeout_flag,
                                   check_point_done_flag,
                                   point_done_seq,
                                   check_timeout,
                                   goto_pnt_action])



        seq.add_child(at_target_fb)

    return seq



if __name__ == '__main__':

    #####################
    # DATA GATHERING SUBTREE
    #####################
    # behaviours that will read some topic from ros topics
    # will go under this
    topics2bb = pt.composites.Sequence("Topics to BB")

    # this will sub to '/abort' and write to 'abort' in the BB of the tree when an Empty is received
    emergency2bb = ptr.subscribers.EventToBlackboard(name='Emergency button',
                                                     topic_name='/abort',
                                                     variable_name='emergency')


    # returns running if there is no data to write until there is data
    # the dict here makes the behaviour write only the .data part of the whole message here
    # into the blackboard variable pitch
    # the clearing policy will not allow the bb variable to be cleared, it'll only be re-written
    # init_variables gives a dict for each bb variable and the value to init it with
    pitch2bb = ptr.subscribers.ToBlackboard(name='Pitch',
                                            topic_name='/pitch_feedback',
                                            topic_type=Float64,
                                            blackboard_variables={'pitch':'data'},
                                            initialise_variables={'pitch':0},
                                            clearing_policy=pt.common.ClearingPolicy.NEVER)

    # same as pitch
    depth2bb = ptr.subscribers.ToBlackboard(name='Depth',
                                            topic_name='/depth_feedback',
                                            topic_type=Float64,
                                            blackboard_variables={'depth':'data'},
                                            initialise_variables={'depth':0},
                                            clearing_policy=pt.common.ClearingPolicy.NEVER)



    # add these to the subtree responsible for data acquisition
    topics2bb.add_children([emergency2bb, pitch2bb, depth2bb])


    #####################
    # SAFETY SUBTREE
    #####################

    # if emergency is False, then we are safe.
    check_safe = pt.blackboard.CheckBlackboardVariable(name="Safe?",
                                                       variable_name='emergency',
                                                       expected_value=False)

    check_safety_tried = pt.blackboard.CheckBlackboardVariable(name="Safety action tried?",
                                                               variable_name='safety_tried',
                                                               expected_value=True)

    # we need the whole msg object to be sent
    emergency_action_msg = GenericStringGoal()
    emergency_action_msg.bt_action_goal = ""
    safety_action = ptr.actions.ActionClient(name='sam_emergency',
                                             action_spec=GenericStringAction,
                                             action_goal=emergency_action_msg,
                                             action_namespace='/sam_emergency')

    set_safety_tried = pt.blackboard.SetBlackboardVariable(name='Set safety tried',
                                                           variable_name='safety_tried',
                                                           variable_value=True)

    attempt_safety = pt.composites.Parallel(name='Attempt safety action')
    attempt_safety.add_children([safety_action, set_safety_tried])


    # TODO make this a function
    safety_pre = pt.composites.Selector(name="Safety precon")
    safety_post = ReactiveSeq(name="Safety postcon")
    safety_post.add_children([check_safety_tried, make_idle()])
    safety_pre.add_children([check_safe, safety_post])

    # tries the safety action once and then idles
    safety_fb = pt.composites.Selector(name='Safety')
    safety_fb.add_children([safety_pre, attempt_safety, make_idle()])


    #####################
    # MISSION SUBTREE
    #####################

    mission_fb = pt.composites.Selector(name='Mission')

    # return SUCCESS if the mission_complete flag is True
    mission_not_complete = pt.blackboard.CheckBlackboardVariable(name='Mission complete?',
                                                                 variable_name='mission_complete',
                                                                 expected_value=True)

    # first check is to see if the mission is complete
    mission_fb.add_child(mission_not_complete)

    # do the mission, if it succeeds, set flag
    mission_exec = ReactiveSeq(name='Mission execution')

    ##############################################################################################
    # ACTUAL MISSION DONE HERE
    ##############################################################################################
    # this mission should be a subtree of behaviour or action client
    #  execute_mission = sam_behaviours.some_mission(name="Execute mission")
    #  execute_mission_msg = GenericStringGoal()
    #  execute_mission_msg.bt_action_goal = ""
    #  execute_mission = ptr.actions.ActionClient(name='execute_mission',
                                             #  action_spec=GenericStringAction,
                                             #  action_goal=execute_mission_msg,
                                             #  action_namespace='/execute_mission')
    execute_mission = make_follow_points_subtree(MISSION_SETPOINTS)
    ##############################################################################################

    set_mission_complete = pt.blackboard.SetBlackboardVariable(name='Set mission complete',
                                                               variable_name='mission_complete',
                                                               variable_value=True)
    # add in order
    mission_exec.add_children([execute_mission, set_mission_complete])
    mission_exec.add_child(execute_mission)
    mission_exec.add_child(set_mission_complete)

    # do mission, if all else fails, idle
    mission_fb.add_child(mission_exec)
    mission_fb.add_child(make_idle())


    # the main meat of the tree
    mission_seq = ReactiveSeq(name='Mission')
    # make the mission
    mission_seq.add_children([safety_fb, mission_fb, make_idle()])


    #####################
    # ROOT
    #####################

    # we want to tick all children at once, namely the topic listeners and
    # the rest of the tree
    root = pt.composites.Parallel("Root")
    # finish the tree by adding the main subtrees to the root
    root.add_children([topics2bb, mission_seq])
    root.add_children([topics2bb])



    rospy.init_node('tree')
    # a nice wrapper for visiting and such
    tree = ptr.trees.BehaviourTree(root)
    # shut down the tree when ctrl-c is received
    shutdown_tree = lambda t: t.interrupt()
    rospy.on_shutdown(functools.partial(shutdown_tree, tree))

    # setup the tree
    if not tree.setup(timeout=10):
        print('TREE COULD NOT BE SETUP')
        sys.exit(1)

    #tree.setup(timeout=10)
    # show the tree's status for every tick
    tick_printer = lambda t: pt.display.print_ascii_tree(t.root, show_status=True)
    # run
    tree.tick_tock(sleep_ms=1000, post_tick_handler=tick_printer)






