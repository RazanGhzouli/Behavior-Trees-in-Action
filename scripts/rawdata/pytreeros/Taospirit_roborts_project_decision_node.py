#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import math
import random
import time

import numpy as np
import rospkg
import rospy
import tf
from decision.msg import EnemyPos
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Odometry
import functools
import py_trees
import py_trees_ros
import py_trees.console as console
from roborts_msgs.msg import (GimbalAngle, GimbalRate, ShootInfo, ShootState,
                              TwistAccel, TeammateMsg)
from tf.transformations import quaternion_from_euler

from battle_env import BattleEnv
from controller import Controller


class TwistControl():
    def __init__(self, move_x, move_y, move_z, angular_z):
        self.Twist = Twist()
        self.Twist.linear.x = move_x
        self.Twist.linear.y = move_y
        self.Twist.linear.z = move_z
        self.Twist.angular.x = 0
        self.Twist.angular.y = 0
        self.Twist.angular.z = angular_z

class BlackBoard():
    def __init__(self):
        self.search_state = False
        self.ForceBuff = False
        self.EnterFollow = False
        self.enemy_last_x = 0
        self.enemy_last_y = 0
        self.enemy_last_yaw = 0
        self.enemy_last_remaining_time = 180

    # gimbal- 0 for track, 1 for patrol, 2 for dodge and track
    # chassis- 0 for normal, 1 for dodge
    # gimbal-chassis：  2-1：进摆尾， 1-0：出摆尾， 0-0：锁定
    def enterDodge(self): # 先进云台，后进底盘
        ctrl.gimbal_mode_switch(2)
        ctrl.chassis_mode_switch(1)
        print ('-----------------!!!!ENTER DODGE!!!!------------------')

    def outDodge(self): # 先出底盘，后出云台
        ctrl.chassis_mode_switch(0)
        ctrl.gimbal_mode_switch(1)
        print ('-------------------!!!!OUT DODGE!!!!------------------')

    def enterTracking(self):
        ctrl.gimbal_mode_switch(0)
        ctrl.chassis_mode_switch(0)
        
    def refreshState(self):
        self.outDodge()
        self.EnterFollow = False
        self.ForceBuff = False

    def twistRotation(self, goal_theta): # battle中的rotation改到这儿，加入云台模式和角度的改变
        env.TwitsRotation(goal_theta)
        print ('-------end rotation--------')
        
    #NOT USE
    def getRangeNum(self, val, border_list):
        if len(border_list) == 1:
            raise Exception('border list is too short')
        border_list.sort()
        for border in border_list: 
            if val > border:
                continue
            return border_list.index(border)
        return len(border_list)

class BuildTree():
    def __init__(self):
        self.blackboard = BlackBoard()
        rate = rospy.Rate(50)
        NORMALBEHAVE = py_trees.composites.Selector("NORMALBEHAVE")
        ROTATE = py_trees.composites.Sequence("ROTATE")
        SUPPLY = py_trees.composites.Sequence("SUPPLY")
        BUFF = py_trees.composites.Sequence("BUFF")
        SEARCH_REGION = py_trees.composites.Sequence("SEARCH")
        FOLLOW = py_trees.composites.Sequence("FOLLOW")

        NORMALBEHAVE.add_child(ROTATE)
        NORMALBEHAVE.add_child(SUPPLY)
        NORMALBEHAVE.add_child(BUFF)
        NORMALBEHAVE.add_child(SEARCH_REGION)
        NORMALBEHAVE.add_child(FOLLOW)

        ISROTATE = IsRotate("ISROTATE", blackboard=self.blackboard)
        ROTATE_DO = Rotate_Do("ROTATE_DO", blackboard=self.blackboard)
        ROTATE.add_child(ISROTATE)
        ROTATE.add_child(ROTATE_DO)

        ISSUPPLY = IsSupply("ISSUPPLY", blackboard=self.blackboard)
        SUPPLY_DO = Supply_Do("SUPPLY_DO",blackboard=self.blackboard)
        SUPPLY.add_child(ISSUPPLY)
        SUPPLY.add_child(SUPPLY_DO)
        
        ISGOTOBUFF = IsGOTOBUFF("ISGOTOBUFF", blackboard=self.blackboard)
        GOTOBUFF = GotoBuff("GOTOBUFF", blackboard=self.blackboard)
        BUFF.add_child(ISGOTOBUFF)
        BUFF.add_child(GOTOBUFF)

        ISSEARCH = IsSearch("ISSERARCH", blackboard=self.blackboard)
        SEARCH = Search("SEARCH", blackboard=self.blackboard)
        SEARCH_REGION.add_child(ISSEARCH)
        SEARCH_REGION.add_child(SEARCH)

        ISFOLLOW = IsFollow("ISFOLLOW", blackboard=self.blackboard)
        FOLLOW_SHOOT = Follow_Shoot("FOLLOW_SHOOT", blackboard=self.blackboard)
        FOLLOW.add_child(ISFOLLOW)
        FOLLOW.add_child(FOLLOW_SHOOT)

        rospy.loginfo("NORMALBEHAVE Tree")
        py_trees.display.print_ascii_tree(NORMALBEHAVE)

        behaviour_tree = py_trees_ros.trees.BehaviourTree(NORMALBEHAVE)
        behaviour_tree.add_pre_tick_handler(self.pre_tick_handler)

        behaviour_tree.visitors.append(py_trees.visitors.DebugVisitor())

        snapshot_visitor = py_trees.visitors.SnapshotVisitor()
        behaviour_tree.add_post_tick_handler(functools.partial(self.post_tick_handler, snapshot_visitor))
        behaviour_tree.visitors.append(snapshot_visitor)

        behaviour_tree.setup(timeout=15)

        while not rospy.is_shutdown():
            try:
                behaviour_tree.tick()
            except KeyboardInterrupt:
                break
            rate.sleep()
        print("\n")


    def pre_tick_handler(self, behaviour_tree):
        print("\n--------- Run %s ---------\n" % behaviour_tree.count)

    def post_tick_handler(self, snapshot_visitor, behaviour_tree):
        print("\n" + py_trees.display.ascii_tree(behaviour_tree.root,
                                                snapshot_information=snapshot_visitor))

class IsRotate(py_trees.Behaviour):
    def __init__(self, name, blackboard = None):
        super(IsRotate,self).__init__(name)
        self.name = name
        self.blackboard = blackboard

    def update(self):
        if env.rotate_at_begining:
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.FAILURE

class Rotate_Do(py_trees.Behaviour):
    def __init__(self, name, blackboard = None):
        super(Rotate_Do,self).__init__(name)
        self.name = name
        self.blackboard = blackboard
        
    def update(self):
        if env.GAME_STATUS != 4:
            return py_trees.Status.SUCCESS
        else:
            rospy.logwarn("****************Rotating****************")
            rotate_start_time = rospy.Time.now().secs
            while rospy.Time.now().secs - rotate_start_time < 3:
                ctrl.send_vel(TwistControl(0, 0, 0, 2).Twist)
            env.rotate_at_begining = False
            return py_trees.Status.FAILURE

class IsSupply(py_trees.Behaviour):
    def __init__(self, name, blackboard = None):
        super(IsSupply,self).__init__(name)
        rospy.loginfo("issupply ready")
        self.name = name
        self.blackboard = blackboard

    def update(self):
        #rospy.INFO("NEED SUPPLY!!!")

        if env.supply_needed == True:
            rospy.loginfo('-------supply_needed is {}'.format(env.supply_needed))
            if not self.blackboard.ForceBuff:
                rospy.loginfo('-------force buff is {}'.format(self.blackboard.ForceBuff))
            #rospy.logwarn("Got supply singal")
                return py_trees.Status.SUCCESS
        else:
            rospy.loginfo('-------supply_needed is {}'.format(env.supply_needed))
            return py_trees.Status.FAILURE

class Supply_Do(py_trees.Behaviour):
    def __init__(self, name, blackboard = None):
        super(Supply_Do,self).__init__(name)
        rospy.loginfo("supply ready")
        self.name = name
        self.blackboard = blackboard
    
    def update(self):
        #rospy.logwarn("got it ")
        #self.blackboard.refreshState()
        env.ARMOR_HIT_NUM = -1
        # if there is no projectile in the supplier and the robot has no projectile
        if env.supply_count == 100 and env.pjt_info == 1: # 自己没足够弹 + 一分钟内补弹已经完毕
            rospy.loginfo('SUPPLY-------supply_count is 100---no supply, self_pjt_info is 1')
            # rotate to defend
            # env.rotate_at_begining = True
        	
            # reset the gimbal angle
            if env.current_gimbal_mode != 2 and env.current_chassis_mode != 1:
                rospy.logwarn('enter dodge mode!')
                ctrl.gimbal_mode_switch(0)
                ctrl.send_gimbal_angle(0.0)
                ctrl.chassis_mode_switch(0)
                # set dodge mode to defend
                ctrl.gimbal_mode_switch(2)
                ctrl.chassis_mode_switch(1)
            
            return py_trees.Status.SUCCESS
        elif env.supply_count == 100 and env.pjt_info == 2: # 自己有弹 + 一分钟内补弹完毕
            rospy.loginfo('SUPPLY------supply_count is 100---no supply, self_pjt_info is 2')
            env.supply_needed = False
            return py_trees.Status.FAILURE    
        elif env.breaksupply:
            rospy.loginfo('SUPPLY------breaksupply is True')
            # break supply to safe place
            if env.isActionAvaliable(env.breakpoint[0], env.breakpoint[1], env.breakpoint[2]):
                env.send_goal_force(env.navgoal)
                env.supply_needed = False
                env.sendgoalresult = False
                env.go_point_num = 2 #-----FIX=------ 0 
                env.breaksupply = False
                env.IS_SUPPLY = 0

                env.rotate_at_begining = True
                
                #env.supply_cooldown = env.REMAINING_TIME
                return py_trees.Status.SUCCESS
        else: # 正常开始进入补给动作
            rospy.logwarn('SUPPLY-----!!!!GO TO SUPPLY!!!!------')
            # cancel dodge mode
            ctrl.chassis_mode_switch(0)
            ctrl.gimbal_mode_switch(1)
            
            # go to default supply place
            if env.go_point_num == 2:
                result = self.nav_to_default_supply_point()

                # cancel dodge mode
                ctrl.chassis_mode_switch(0)
                ctrl.gimbal_mode_switch(1)

                if result:
                    rospy.logwarn("SUPPLY------!!!finish supply!!!-------")
                    env.supply_needed = False
                    env.sendgoalresult = False
                    #----fix------2019.05.20
                    env.go_point_num = 2
                    #----fix----
                    env.IS_SUPPLY = 0
                    env.supply_cooldown = env.REMAINING_TIME
                    return py_trees.Status.SUCCESS
                else:
                    if env.breaksupply: # 血少中断补给 
                        return py_trees.Status.SUCCESS
                    else: # 超时未达
                        rospy.logwarn("default supply fail")
                        env.supply_needed = False
                        env.sendgoalresult = False
                        env.go_point_num = 2
                        env.IS_SUPPLY = 0
                        env.supply_cooldown = env.REMAINING_TIME
                        return py_trees.Status.SUCCESS
            else:
                while env.supply_needed :
                    env.IS_SUPPLY = 1
                    supplypoint = env.supplypoint_list[env.go_point_num]
                    rospy.logwarn('IS_SUPPLY is 1, supply_point is {:.2f}, {:.2f}, {:.2f}'.format(supplypoint[0], supplypoint[1], supplypoint[2]))
                    
                    if env.isActionAvaliable(supplypoint[0], supplypoint[1], supplypoint[2]):
                        env.send_goal_force(env.navgoal)
                        goal_start = time.time()

                        if env.sendgoalresult:
                            env.tag_info = {'tag_detected': False, 'x': 0, 'z': 0, 'pitch': 0, 'distance': 0 }
                            rospy.loginfo("got the supply area!")
                            find_start = time.time()
                            # if do not detect the tag, rotate
                            while env.tag_info['tag_detected'] == False:
                                if env.ARMOR_HIT_NUM != -1 and env.REMAIN_HP < 300: 
                                    env.breaksupply = True
                                    return py_trees.Status.SUCCESS
                                else:
                                    rotate_end = time.time()
                                    if rotate_end - find_start < 2:
                                        ctrl.send_vel(cmdvel_slowyoutwist)
                                    elif rotate_end - find_start >= 2 and rotate_end - find_start < 6:
                                        ctrl.send_vel(cmdvel_slowzuotwist)
                                    else:
                                        # change supply point
                                        if env.go_point_num == 0:
                                            env.go_point_num = 1
                                            rospy.logwarn("tag not found!!!!!!! go to the next point")
                                            return py_trees.Status.SUCCESS
                                        else:
                                            env.go_point_num = 2
                                            return py_trees.Status.SUCCESS
                            
                            #reset the gimbal angle
                            ctrl.gimbal_mode_switch(0)
                            ctrl.send_gimbal_angle(0.0)
                            ctrl.chassis_mode_switch(0)

                            # adjust the pitch angle
                            find_start = time.time()
                            while abs(env.tag_info['pitch']) > 2:
                                rotate_end = time.time()
                                if rotate_end - find_start < 3:
                                    if env.ARMOR_HIT_NUM != -1 and env.REMAIN_HP < 300: 
                                        env.breaksupply = True
                                        return py_trees.Status.SUCCESS
                                    else:
                                        if env.tag_info['pitch'] > 0:
                                            ctrl.send_vel(cmdvel_slowyoutwist)
                                        elif env.tag_info['pitch'] < 0:
                                            ctrl.send_vel(cmdvel_slowzuotwist)
                                        rospy.logwarn("angle: ")
                                        rospy.loginfo(env.tag_info['pitch'])
                                else:
                                    if env.go_point_num == 0:
                                        env.go_point_num = 1
                                        rospy.logwarn("tag angle not appropriate!!!!!!! go to the next point")
                                        return py_trees.Status.SUCCESS
                                    else:
                                        env.go_point_num = 2
                                        return py_trees.Status.SUCCESS

                            # adjust the x distance 
                            find_start = time.time()            
                            while abs(env.tag_info['x']) > 0.1:
                                move_end = time.time()
                                if move_end - find_start < 2:
                                    if env.ARMOR_HIT_NUM != -1 and env.REMAIN_HP < 300: 
                                        env.breaksupply = True
                                        return py_trees.Status.SUCCESS
                                    else:
                                        ctrl.send_vel(TwistControl(0, 0.5*(env.tag_info['x']/abs(env.tag_info['x'])), 0, 0).Twist)
                                        rospy.logwarn("zuoyou distance: ")
                                        rospy.loginfo(env.tag_info['x'])
                                else:
                                    if env.go_point_num == 0:
                                        env.go_point_num = 1
                                        rospy.logwarn("tag x move wrong!!!!!!! go to the next point")
                                        return py_trees.Status.SUCCESS
                                    else:
                                        env.go_point_num = 2
                                        return py_trees.Status.SUCCESS
                            
                            # adjust the z distance 
                            find_start = time.time()  
                            while env.tag_info['z'] > 0.7:
                                move_end = time.time()
                                if move_end - find_start < 3:
                                    if env.ARMOR_HIT_NUM != -1 and env.REMAIN_HP < 300:
                                        env.breaksupply = True
                                        return py_trees.Status.SUCCESS
                                    else:
                                        # backward
                                        ctrl.send_vel(TwistControl(-0.5, 0, 0, 0).Twist)
                                        rospy.logwarn("moving!!!")
                                        rospy.loginfo(env.tag_info['z'])
                                else:
                                    if env.go_point_num == 0:
                                        env.go_point_num = 1
                                        rospy.logwarn("tag z move wrong!!!!!!! go to the next point")
                                        return py_trees.Status.SUCCESS
                                    else:
                                        env.go_point_num = 2
                                        return py_trees.Status.SUCCESS

                            rospy.logwarn("reached supply area")
                            rospy.loginfo("************supplying**************")
                            env.supplytalker.publish(env.supply_amount)
                            supply_start = time.time()

                            # set dodge mode
                            ctrl.gimbal_mode_switch(2)
                            ctrl.chassis_mode_switch(2)

                            while(True):
                                supply_end = time.time()
                                if supply_end - supply_start < 5:
                                    if env.ARMOR_HIT_NUM != -1 and env.REMAIN_HP < 300: 
                                        env.breaksupply = True
                                        return py_trees.Status.SUCCESS 
                                    else:
                                        pass
                                else:
                                    rospy.logwarn("supplying done")
                                    env.supply_needed = False
                                    env.sendgoalresult = False
                                    env.go_point_num = 0
                                    env.IS_SUPPLY = 0
                                    env.supply_cooldown = env.REMAINING_TIME

                                    # cancel dodge mode
                                    ctrl.chassis_mode_switch(0)
                                    ctrl.gimbal_mode_switch(1)
                                    return py_trees.Status.SUCCESS
                        
                        else:
                            goal_end = time.time()
                            if goal_end - goal_start > 8 :
                                if env.go_point_num == 0:
                                    env.go_point_num = 1
                                    return  py_trees.Status.SUCCESS
                                else :
                                    env.go_point_num = 2
                                    return py_trees.Status.SUCCESS
                            else:
                                pass
                    else:
                        if env.go_point_num == 0:
                            env.go_point_num = 1
                            rospy.logwarn("tag not found!!!!!!! go to the next point")
                            return py_trees.Status.SUCCESS
                        else:
                            env.go_point_num = 2
                            return py_trees.Status.SUCCESS

    
    def nav_to_default_supply_point(self):
        supplypoint = env.supplypoint_default
        if env.isActionAvaliable(supplypoint[0], supplypoint[1], supplypoint[2]):
            env.IS_SUPPLY = 1

            env.SUPPLY_cancle_flag = 0
            env.send_goal_in_supply(env.navgoal)

            if env.SUPPLY_cancle_flag == 1:
                return False
            
            # reset the gimbal angle
            ctrl.gimbal_mode_switch(0)
            ctrl.send_gimbal_angle(0.0)
            ctrl.chassis_mode_switch(0)
          
            go_default_start = rospy.Time.now().secs
            
            if env.sendgoalresult:
                twist_start_time = rospy.Time.now().secs

                while abs(520 - env.deepth_behind) > 50 and rospy.Time.now().secs - twist_start_time < 3:
                    sign = (-1 if (env.deepth_behind > 520) else 1)

                    # if (520 - env.deepth_behind) > 0:
                    #     sign = 1
                    # else:
                    #     sign = 0
                    # sign = (520 - env.deepth_behind) / abs(520 - env.deepth_behind)
                    rospy.logwarn('deepth_behind distance is {:.3f}, delta is {:.3f}'.format(env.deepth_behind, 600 - env.deepth_behind))
                    ctrl.send_vel(TwistControl(0.3 * sign, 0, 0, 0).Twist)

                rospy.logwarn("SUPPLY--------!!!!reached default supply area!!!!--------")
                rospy.loginfo("************supplying**************")
                # have arrived supply area
                env.supplytalker.publish(env.supply_amount)
                # wait for supply in supply area
                while(True):

                    if env.ARMOR_HIT_NUM != -1 and env.REMAIN_HP < 300: 
                        env.breaksupply = True
                        return False
                    
                    if rospy.Time.now().secs - go_default_start < 8:
                        if env.SUPPLIER_STATUS == 2:
                            rospy.sleep(2)
                            return True
                        else:
                            pass
                    else:
                        return False

                    # if rospy.Time.now().secs - go_default_start < 4:
                    #     if env.ARMOR_HIT_NUM != -1 and env.REMAIN_HP < 300: 
                    #         env.breaksupply = True
                    #         return False
                    #     else:
                    #         pass
                    # else:
                    #     return True
            else:
                if rospy.Time.now().secs - go_default_start > 7:
                    rospy.logwarn("!!!!!!!the area is not reachable!!!!!!!!!!!!supply failed!!!!!!!!!!!")
                    return False
                else:
                    pass
        else:
            rospy.logwarn('Action is not avaliable!!!!!!!')
            return False

class IsGOTOBUFF(py_trees.Behaviour):
    def  __init__(self, name, blackboard=None):
        super(IsGOTOBUFF, self).__init__(name)
        self.name = name
        self.blackboard = blackboard
    def update(self):
        if env.buff_needed:
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.FAILURE

class GotoBuff(py_trees.Behaviour):
    def __init__(self, name, blackboard=None):
        super(GotoBuff, self).__init__(name)
        self.name = name
        self.blackboard = blackboard
        self.start_buff = 0
        self.buff_point = [6.3, 1.75, 150]
        self.remain_time = 7
        self.not_arrived_dist = 0.5
        #self.buff_first_hited = False

    def update(self):
        rospy.logwarn('****************ENTER GotoBuff****************')
        rospy.loginfo("----------count num is {}---------".format(env.gotobuff_count))
        # print ('forcebuff is {}'.format(self.blackboard.ForceBuff))

        #------fix-------2019.05.17添加：直接切search然后直接切fellow
        dist_to_buff = math.hypot(env.robot_pose['x'] - self.buff_point[0], env.robot_pose['y'] - self.buff_point[1])
        if dist_to_buff < 1: # 距离buff点大于1米，不响应敌人信息，取完buff再走
            rospy.logwarn('________near buff area, GO BUFF FORCE!________')
            pass
        elif env.detection_result: # 相机监测到，跟随敌人行动
            rospy.logwarn('________NOT near, detect when enter buff________')
            dist_enemy = math.hypot(env.robot_pose['x'] - env.enemy_position['x'], env.robot_pose['y'] - env.enemy_position['y'])
            if dist_enemy < 2:
                rospy.logerr('______enemy in {:.2f} meters for robot, ENTER SEARCH______'.format(dist_enemy))
                return py_trees.Status.FAILURE
            else:
                pass
        #------fix-------------

        if not self.blackboard.ForceBuff: # ForceBuff初始化为false,是为了在取BUFF中屏蔽SUPPLY
            self.blackboard.outDodge()
            self.blackboard.EnterFollow = False
            self.blackboard.ForceBuff = False
    
        if env.SELF_BONUS_STATUS == 0:
            # rospy.loginfo("BUFF---{}---going to BUFF!!!!".format(env.COLOR))
            if not (self.isInRange(env.robot_pose['x'], 6.1, 6.5) and self.isInRange(env.robot_pose['y'], 1.25, 1.95)):
                self.buff_point[2] = math.degrees(math.atan2(self.buff_point[1]-env.robot_pose['y'],self.buff_point[0]-env.robot_pose['x']))
                if env.isActionAvaliable(self.buff_point[0], self.buff_point[1], self.buff_point[2]):
                    if env.pjt_info != 3:
                        env.BUFF_cancle_flag = 0
                        env.send_goal_buff_force(env.navgoal) # 弹量少时force_send_goal
                        
                        if env.BUFF_cancle_flag == 1:
                            rospy.loginfo('BUFF---{}---BUFF is getting by other robot, cancle goal!'.format(env.COLOR))
                            return py_trees.Status.FAILURE

                    else: # 弹药充足
                        env.BUFF_cancle_flag = 0
                        env.send_goal_buff(env.navgoal)
                    
                        if env.BUFF_cancle_flag == 1:
                            rospy.loginfo('BUFF---{}---BUFF is getting by other robot, cancle goal!'.format(env.COLOR))
                            return py_trees.Status.FAILURE

                        if env.BUFF_cancle_flag == 2:
                            rospy.loginfo('BUFF---{}---detect enemy for good distance during goto BUFF, cancle goal!'.format(env.COLOR))
                            return py_trees.Status.SUCCESS # 重进行为树，继续取buff

                    #-----have finlished send_goal

                    dist_me = math.hypot(env.robot_pose['x']-env.navgoal.goal.pose.position.x, env.robot_pose['y']-env.navgoal.goal.pose.position.y)
                    if dist_me > self.not_arrived_dist:
                        rospy.logwarn('cannot goto buff area')
                        env.gotobuff_count += 1
                        return py_trees.Status.SUCCESS

                    self.start_buff = rospy.Time.now().secs
                    self.blackboard.ForceBuff = True # 取buff时暂时屏蔽supply

                    if env.current_gimbal_mode != 2 and env.current_chassis_mode != 1:
                        self.blackboard.twistRotation(150)
                        
                    return py_trees.Status.SUCCESS
                else:
                    return py_trees.Status.FAILURE
            else:
                # robot have be in BUFF area but BONUS_STATUS is still 0
                stay_time = rospy.Time.now().secs - self.start_buff
                if env.detection_result:
                    if env.current_gimbal_mode != 2 and env.current_chassis_mode != 1: # point to enemy when not dodge
                        env.getEnemyDirection()
                        self.blackboard.twistRotation(env.twist_goal_theta)
                       
                        rospy.loginfo('______!!!!!first_rotation!!!!!______(0)')
                    if env.detection_result_front:
                        rospy.logwarn("______detect enemy by front, START DODGE______(0)")
                        self.blackboard.enterDodge()
                        # env.chassis_mode = 1
                        # env.gimbal_mode = 2
                #响应被打
                elif env.ARMOR_HIT_NUM != -1:
                    if env.current_gimbal_mode != 2 and env.current_chassis_mode != 1:
                        env.getEnemyDirection()
                        self.blackboard.twistRotation(env.twist_goal_theta)
                       
                        env.ARMOR_HIT_NUM = -1
                print ('--------------------------retry--------------------------')

                if stay_time < self.remain_time + 3:
                    print ('********robot is in buff aere, buff status: {}, wait for {}s********'.format(env.SELF_BONUS_STATUS, stay_time))
                    return py_trees.Status.SUCCESS
                else:
                    print ('********robot cannot get buff in buff area(0), time {}s out********'.format(self.remain_time + 3))
                    return py_trees.Status.FAILURE

        elif env.SELF_BONUS_STATUS == 1:
            if self.isInRange(env.robot_pose['x'], 5.8, 6.8) and self.isInRange(env.robot_pose['y'], 1.25, 2.3):

                stay_time = rospy.Time.now().secs - self.start_buff
                if env.detection_result:
                    if env.current_gimbal_mode != 2 and env.current_chassis_mode != 1: # point to enemy when not dodge
                        env.getEnemyDirection()
                        self.blackboard.twistRotation(env.twist_goal_theta)
                        
                        print ('______!!!!!first_rotation!!!!!______(1)')
                    if env.detection_result_front:
                        rospy.logwarn("______detect enemy by front, START DODGE______(1)")
                        self.blackboard.enterDodge()
                        # env.chassis_mode = 1
                        # env.gimbal_mode = 2
                #响应被打
                elif env.ARMOR_HIT_NUM != -1:
                    if env.current_gimbal_mode != 2 and env.current_chassis_mode != 1:
                        env.getEnemyDirection()
                        self.blackboard.twistRotation(env.twist_goal_theta)
                       
                        env.ARMOR_HIT_NUM = -1
                print ('--------------------------retry--------------------------')

                if stay_time < self.remain_time:
                    print ('********robot getting buff in buff area, buff status: {}, wait for {}s********'.format(env.SELF_BONUS_STATUS, stay_time))
                    return py_trees.Status.SUCCESS
                else:
                    print ('********robot cannot get buff in buff area(1), time {}s out********'.format(self.remain_time))
                    return py_trees.Status.FAILURE

            else:
                rospy.loginfo('Buff is {}, somebody is getting buff, OUT!'.format(env.SELF_BONUS_STATUS))
                return py_trees.Status.FAILURE

        # return py_trees.Status.FAILURE
        # rospy.logwarn('BUFF--------TIME OUT----------')
        # self.buff_first_hited = False
        # self.blackboard.outDodge()
        # self.blackboard.ForceBuff = True
        # return py_trees.Status.FAILURE
                        
    def isInRange(self, val, val1, val2):
        if val < val1:
            return False
        elif val > val2:
            return False
        return True

class IsSearch(py_trees.Behaviour):
    def __init__(self, name, blackboard=None):
        super(IsSearch, self).__init__(name)
        self.name = name
        self.blackboard = blackboard

    def update(self):
        if not self.blackboard.EnterFollow:
            return py_trees.Status.SUCCESS
        else:
            rospy.logwarn('**********ENTER_FOLLOW is true, enter FOLLOW!**********')
            return py_trees.Status.FAILURE

class Search(py_trees.Behaviour):
    def __init__(self, name, blackboard=None):
        super(Search, self).__init__(name)
        self.name = name 
        self.blackboard = blackboard
        self.closed_list = []
        self.rotation_theta_threshold = 20 # 计算底盘朝向和其与敌人连线夹角，移动中大于该阈值时才转向指向敌人
        self.enemy_buff_point = [1.7, 3.25] # enemy buff center in map
        self.search_enemy = False
        # self.search_cmd = False
        self.search_buff = False
        # self.search_order = [0, 1, 2, 3]

    def update(self):
        print('\n\n-----------------Robot BUFF is {}, MAP BUFF is {}----------------'.format(env.ROBOT_BONUS, env.SELF_BONUS_STATUS))

        if env.detected_by_front: # 满足FOLLOW条件直接切
            dist_enemy = math.hypot(env.robot_pose['x'] - env.enemy_position['x'], env.robot_pose['y'] - env.enemy_position['y'])
            if dist_enemy < env.SEARCH_stop_dist:
                self.blackboard.EnterFollow = True
                return py_trees.Status.FAILURE

        print ('************************ENTER SEARCH**************************')
        self.blackboard.outDodge()
        self.blackboard.EnterFollow = False
        self.blackboard.ForceBuff = False
        print ('____________refresh state____________')
        
        location_num = self.getLocationNum()
        if len(self.closed_list) >= len(env.search_regions[location_num]):
            location_num += 1
            location_num %= len(env.search_regions)
            rospy.loginfo("search region {} is clear, going to region {}".format(location_num-1, location_num))
            self.closed_list = []

        goal_x, goal_y, goal_theta = self.getPointToGo(env.search_regions[location_num])

        if not env.isActionAvaliable(goal_x, goal_y, goal_theta, 0):
            rospy.logwarn("cannot goto point {:.2f}, {:.2f} with {:.2f}".format(goal_x, goal_y, goal_theta))
            if [goal_x, goal_y, goal_theta] in env.search_regions[location_num]:
                self.closed_list.append([goal_x, goal_y, goal_theta])
        else:
            if self.search_enemy:
                self.closed_list[:] = []
                if abs(goal_theta - env.robot_pose['theta']) > self.rotation_theta_threshold:
                    rospy.logwarn('Rotation for point to enemy')
                    self.blackboard.twistRotation(goal_theta)
                    #---fix----2019.05.19
                    # self.blackboard.outDodge() # 转完后云台重新patrol  
                    #---fix----
                rospy.logwarn('Goto enemy point {:.2f}, {:.2f} with {:.2f}'.format(goal_x, goal_y, goal_theta))
            elif self.search_buff:
                self.closed_list[:] = []
                rospy.loginfo('Goto buff point {:.2f}, {:.2f} with {:.2f}'.format(goal_x, goal_y, goal_theta))
            else:
                rospy.loginfo('Goto search point {:.2f}, {:.2f} with {:.2f}'.format(goal_x, goal_y, goal_theta))

            env.SEARCH_cancel_flag = 0
            env.send_goal_in_search(env.navgoal)

            while env.SEARCH_cancel_flag == 1 and env.is_blocked:
                env.getEscaspeDirection()
                rospy.logwarn('try to escaspe in SEARCH!')
                ctrl.send_vel(TwistControl(env.escape_v_x, env.escape_v_y, 0, 0).Twist)

            self.blackboard.enemy_last_x, self.blackboard.enemy_last_y = 0, 0
            if env.SEARCH_cancel_flag == 2: # supply needed out
                return py_trees.Status.SUCCESS

            if env.SEARCH_cancel_flag == 3: # close out
                rospy.sleep(0.1)
                if env.detected_by_front:
                    print ('_______________the enemy detected by front, enter follow!!_______________')
                    self.blackboard.EnterFollow = True
                    return py_trees.Status.FAILURE
                else:
                    print ('_______________close but not detected by front, retry!_______________')
                    return py_trees.Status.SUCCESS

            if env.SEARCH_cancel_flag == 4: # detect and refresh enemy position
                return py_trees.Status.SUCCESS

            if env.SEARCH_cancel_flag == 5: # not detect but hit, rotation
                env.getEnemyDirection()
                self.blackboard.twistRotation(env.twist_goal_theta)
                # #---fix----2019.05.19
                # self.blackboard.outDodge()
                # #---fix----
                env.ARMOR_HIT_NUM = -1
                return py_trees.Status.SUCCESS

            if env.SEARCH_cancel_flag == 6: # find enemy in buff and rotation self to point to
                rospy.loginfo('-------rotation to enemy buff area-------')
                point_theta = math.degrees(math.atan2(self.enemy_buff_point[1] - env.robot_pose['y'], self.enemy_buff_point[0] - env.robot_pose['x']))
                self.blackboard.twistRotation(point_theta)
                #---fix----2019.05.19
                # self.blackboard.outDodge()
                #---fix----
                return py_trees.Status.SUCCESS

            #XXX: cooperation with teammate
            if env.SEARCH_cancel_flag == 7:
                # point_theta = math.degrees(math.atan2(env.MATE_POSE['y'] - env.robot_pose['y'], env.MATE_POSE['x'] - env.robot_pose['x']))
                # env.TwitsRotation(point_theta)
                rospy.logwarn('--------goto enemy pose from mate info----------')
                return py_trees.Status.SUCCESS

            if env.SEARCH_cancel_flag == 10: # search points smoothly
                print ('SEARCH: enemy-{}, buff-{}'.format(self.search_enemy, self.search_buff))
                # 3种情况，search_enemy, search_buff, search_region
                if self.search_enemy:
                    return py_trees.Status.SUCCESS
                else:
                    self.blackboard.twistRotation(goal_theta)
                    # #---fix----2019.05.19
                    # self.blackboard.outDodge()
                    # #---fix----
                    if not self.search_buff:
                        self.closed_list.append([goal_x, goal_y, goal_theta])
                    return py_trees.Status.SUCCESS

            if env.SEARCH_cancel_flag == 0:
                self.closed_list.append([goal_x, goal_y, goal_theta])

        return py_trees.Status.SUCCESS

    def getLocationNum(self): # get region number robot in
        if env.robot_pose['y'] < 2.5:
            if env.robot_pose['x'] < 3.5:
                return 0
            else:
                return 3
        elif env.robot_pose['x'] < 4.5:
            return 1
        else:
            return 2

    def getPointToGo(self, open_list):
        self.search_enemy = False
        self.search_buff = False
        env.SEARCH_answer_enemy_buff = False
        # self.search_cmd = False
        # detecte event
        if env.detection_result:
            if env.isInMap(env.enemy_position['x'], env.enemy_position['y']):
                self.search_enemy = True
                rospy.logwarn('-----find enemy and go!-----')
                point_theta = math.degrees(math.atan2(env.enemy_position['y'] - env.robot_pose['y'], env.enemy_position['x'] - env.robot_pose['x']))
                return env.enemy_position['x'], env.enemy_position['y'], point_theta
            else:
                print ("---enemy_position detected is out map----")
            # return self.getNearPoint(env.enemy_position['x'], env.enemy_position['y'], 1.0)
        # follow last pose
        if self.blackboard.enemy_last_x != 0 or self.blackboard.enemy_last_y != 0:
            self.search_enemy = True
            rospy.logwarn('----go last enemy position to search-----')
            point_theta = math.degrees(math.atan2(self.blackboard.enemy_last_y - env.robot_pose['y'], self.blackboard.enemy_last_x - env.robot_pose['x']))
            return self.blackboard.enemy_last_x, self.blackboard.enemy_last_y, point_theta
        
        # enemy getting buff event
        if env.ENEMY_BONUS_STATUS == 1 and not env.SEARCH_answer_enemy_buff: # have rotation point to buff center point, but cannot detect any enemy
            near_x, near_y, near_theta = self.getCloestPointFromMe(env.search_buff_point)
            if math.hypot(near_x - env.robot_pose['x'], near_y - env.robot_pose['y']) < 0.5:
                print ('---robot have been search enemy buff point, but no enemy in sight----')
                env.SEARCH_answer_enemy_buff = True
                # rospy.sleep(0.2)
            else:
                self.search_buff = True
                rospy.logwarn('----go to cloest point to search buff area-----')
                return near_x, near_y, near_theta
        # enemy position get from MATE
        if env.ENEMY_POSE_FROM_MATE['x'] != 0 and env.ENEMY_POSE_FROM_MATE['y'] != 0: # get enemy position from MATE
            self.search_enemy = True
            rospy.logwarn('-----search enemy position from MATE info----')
            point_theta_from_mate = math.degrees(math.atan2(env.ENEMY_POSE_FROM_MATE['y'] - env.robot_pose['y'], env.ENEMY_POSE_FROM_MATE['x'] - env.robot_pose['x']))
            return env.ENEMY_POSE_FROM_MATE['x'], env.ENEMY_POSE_FROM_MATE['y'], point_theta_from_mate

        # choose search point
        if not self.closed_list: # if closed_list is empty, it mean I search enemy or search buff just now
            close_x, close_y, close_theta = self.getCloestPointFromMe(open_list)
            open_list_index = open_list.index([close_x, close_y, close_theta])
            for i in range(0, open_list_index):
                self.closed_list.append(open_list[i])

        for p in open_list:
            if p in self.closed_list:
                continue
            else:
                rospy.logwarn('-----search near region point -----')
                return p[0], p[1], p[2] # return x, y, theta

    def getCloestPointFromMe(self, open_list):
        dist_min = float('inf')
        p_min = []
        for p in open_list:
            dist = math.hypot(env.robot_pose['x'] - p[0], env.robot_pose['y'] - p[1])
            if dist < dist_min:
                dist_min = dist
                p_min = p
        print ('p_min is {}'.format(p_min))
        return p_min[0], p_min[1], p_min[2]

    def getNearPoint(self, pose_x, pose_y, dist = 1): # 获取离pose距离dist且距离障碍物安全距离的点
        choose_point = []
        enemy_theta = math.degrees(math.atan2(pose_y - env.robot_pose['y'], pose_x - env.robot_pose['x']))
        choose_point.append([pose_x, pose_y, enemy_theta])

        for t in range(-180, 180, 1):
            x = pose_x + dist * math.cos(math.radians(t))
            y = pose_y + dist * math.sin(math.radians(t))
            
            if not env.isReachable(pose_x, pose_y, x, y):
                continue
            if env.isNear(x, y):
                continue
            theta = math.degrees(math.atan2(y - env.robot_pose['y'], x - env.robot_pose['x']))
            choose_point.append([x, y, theta])
        
        return self.getCloestPointFromMe(choose_point)
       
    def getHelpPointToMate(self):
        point_theta = math.degrees(math.atan2(env.MATE_POSE['y'] - env.robot_pose['y'], env.MATE_POSE['x'] - env.robot_pose['x']))
        return env.MATE_POSE['x'], env.MATE_POSE['y'], point_theta

class IsFollow(py_trees.Behaviour):
    def __init__(self, name, blackboard=None):
        super(IsFollow, self).__init__(name)
        self.name = name
        self.blackboard = blackboard

    def update(self):
        if self.blackboard.EnterFollow == True:
            #rospy.loginfo('FALLOW: {}'.format(env.enemy_pose.dist))
            return py_trees.Status.SUCCESS
        else:
            return py_trees.Status.FAILURE

class Follow_Shoot(py_trees.Behaviour):
    def __init__(self, name, blackboard=None):
        super(Follow_Shoot, self).__init__(name)
        self.name = name
        self.blackboard = blackboard
        self.goal_x = 0.01
        self.goal_y = 0.01
        self.goal_yaw = 0
        self.yaw = 0
        self.keep_length = 0
        self.time1 = 0
        self.change_angle_list = [0, 0, 5, -5, 10, -10, -17, 17, 24, -24, 32, -32, 40, -40, 50, -50, 60, -60]
        self.no_big_change = False
        self.first_enter_stable = True

    def update(self):
        rospy.loginfo('---------ENTER FOLLOW_SHOOT-----------')
        if env.detection_result_front == False:
            ctrl.send_vel(TwistControl(0, 0, 0, 0).Twist)
            self.blackboard.EnterFollow = False
            return py_trees.Status.FAILURE

        self.blackboard.enemy_last_x = env.enemy_position['x']
        self.blackboard.enemy_last_y = env.enemy_position['y']
        self.blackboard.enemy_last_yaw = env.enemy_pose.enemy_yaw
        self.blackboard.enemy_last_remaining_time = env.REMAINING_TIME
            
        if (env.detected_by_front == True and env.enemy_pose.enemy_dist < 1.5 and env.enemy_pose.enemy_dist > 0.7) or (
            env.detected_by_front == False and env.num_not_detected_enemy_front < 10): 
            self.blackboard.enterDodge()
            return py_trees.Status.SUCCESS
        elif ((env.enemy_pose.enemy_dist > 2.0 or env.enemy_pose.enemy_dist <= 0.4) and env.detected_by_front == True) or env.num_not_detected_enemy_front > 15:
            self.blackboard.enterTracking()
        else:
            return py_trees.Status.SUCCESS

        if env.detected_by_front == False:
            return py_trees.Status.SUCCESS

        if self.follow_goal(env.enemy_pose.enemy_dist, env.enemy_pose.enemy_yaw, env.enemy_position['x'], 
            env.enemy_position['y'], env.robot_pose['x'], env.robot_pose['y']) == False:
            if self.rescue_follow_goal(env.enemy_position['x'], env.enemy_position['y'], env.enemy_pose.enemy_yaw, 
                    env.robot_pose['x'], env.robot_pose['y']) == False:
                self.blackboard.EnterFollow = False
                return py_trees.Status.FAILURE # 无法跟随 

        if env.isActionAvaliable(self.goal_x, self.goal_y,
                                        self.normalizeDegree(self.goal_yaw)):  # 判断目标点是否可行
            env.enemy_follow_x = env.enemy_position['x']
            env.enemy_follow_y = env.enemy_position['y']
            env.send_goal_in_follow(env.navgoal)
            rospy.loginfo('r0: is follow !!!!!!!     %s,%s,%s' %
                                (self.goal_x, self.goal_y, self.normalizeDegree(self.goal_yaw)))
        if env.FOLLOW_cancel_flag == 1:
            self.blackboard.EnterFollow = False
            return py_trees.Status.FAILURE
        return py_trees.Status.SUCCESS

    # def need_change_angle(self, angle_min, angle_max): # degrees
    #     angle = abs(math.degrees(env.enemy_pose.enemy_yaw) - env.robot_pose['theta'])
    #     if angle <= angle_max and angle >= angle_min:
    #         return False
    #     else:
    #         return True

    def follow_goal(self, enemy_dist, enemy_yaw, enemy_x, enemy_y, robot_x, robot_y):
        rospy.logerr("---------follow_goal---------")
        self.count = 0
        self.change_angle = 0
        self.goal_x = 0.01
        self.goal_y = 0.01
        self.goal_yaw = 0

        if self.close_obstacle(enemy_x, enemy_x, robot_x, robot_y, 0.3) == True:
            self.keep_length = 1
        elif enemy_dist > 0 and enemy_dist < 3:
            self.keep_length = 1.2 # 跟随距离
        
        while env.isActionAvaliable(self.goal_x, self.goal_y, self.normalizeDegree(self.goal_yaw)) == False:
            self.count += 1
            if self.count > (len(self.change_angle_list) - 1):
                rospy.logwarn('!!!!!!  cant follow  !!!!!!!')
                return False     # 无法跟随         
            self.change_angle = math.radians(self.change_angle_list[self.count]) # 旋转角度 radian
                    
            rospy.loginfo("%s" % math.degrees(self.change_angle))
            self.yaw = enemy_yaw + self.change_angle - math.pi
            self.goal_x = self.keep_length * math.cos(self.yaw) + enemy_x
            self.goal_y = self.keep_length * math.sin(self.yaw) + enemy_y
            self.goal_yaw = self.yaw - math.pi
            
            if self.obstacle_dis(self.goal_x, self.goal_y, 0.4) == False or env.isReachable(enemy_x, enemy_y, 
                 self.goal_x, self.goal_y) == False:
                self.goal_x = 0.01
                self.goal_y = 0.01
        return True
    
    def rescue_follow_goal(self, enemy_x, enemy_y, enemy_yaw, robot_x, robot_y):
        if enemy_yaw >= math.pi/2:
            self.goal_x = robot_x
            self.goal_y = enemy_y
            self.goal_yaw = math.radians(178)
            if env.isReachable(self.goal_x, self.goal_y, robot_x, robot_y) == False:
                self.goal_x = enemy_x
                self.goal_y = robot_y
                self.goal_yaw = math.radians(90)
        elif enemy_yaw >= 0:
            self.goal_x = robot_x
            self.goal_y = enemy_y
            self.goal_yaw = 0.01
            if env.isReachable(self.goal_x, self.goal_y, robot_x, robot_y) == False:
                self.goal_x = enemy_x
                self.goal_y = robot_y
                self.goal_yaw = math.radians(90)
        elif enemy_yaw >= -math.pi/2:
            self.goal_x = robot_x
            self.goal_y = enemy_y
            self.goal_yaw = 0.01
            if env.isReachable(self.goal_x, self.goal_y, robot_x, robot_y) == False:
                self.goal_x = enemy_x
                self.goal_y = robot_y
                self.goal_yaw = math.radians(-90)         
        else:
            self.goal_x = robot_x
            self.goal_y = enemy_y
            self.goal_yaw = math.radians(178)
            if env.isReachable(self.goal_x, self.goal_y, robot_x, robot_y) == False:
                self.goal_x = enemy_x
                self.goal_y = robot_y
                self.goal_yaw = math.radians(-90)
        if env.isActionAvaliable(self.goal_x, self.goal_y, self.normalizeDegree(self.goal_yaw)) == False:
            return False
        else:
            return True

    def normalizeDegree(self, theta): # 将角度radian归一化为[-180, 180]
        return math.degrees(math.atan2(math.sin(theta), math.cos(theta)))

    # def enemy_big_change(self):
    #     if np.square(self.blackboard.enemy_last_x - env.enemy_position['x']) + np.square(self.blackboard.enemy_last_y - env.enemy_position['y']) < 0.025:
    #         return False
    #     if abs(math.degrees(env.enemy_pose.enemy_yaw) - env.robot_pose['theta']) < 40:
    #         return False
    #     return True

    def obstacle_dis(self, robot_x, robot_y, dis_set):
        dis_min = 10
        for i in env.obstacle_conner:
            dis = math.hypot(robot_x - i[0], robot_y - i[1])
            if dis < dis_min:
                dis_min = dis
        if dis_min < dis_set:
            return False
        else:
            return True
    
    def close_obstacle(self, enemy_x, enemy_y, robot_x, robot_y, dis_set):
        dis_min = 10
        for i in env.obstacle_conner:
            if self.judge(i[0], i[1], enemy_x, enemy_y, robot_x, robot_y):
                dis = self.dis_point_to_line(i[0], i[1], enemy_x, enemy_y, robot_x, robot_y)
                if dis_min > dis:
                    dis_min = dis
        if dis_min < dis_set:
            return True
        else:
            return False
    
    def dis_point_to_line(self, pointX, pointY, lineX1, lineY1, lineX2, lineY2): # 一般式
        a = lineY2 - lineY1
        b = lineX1 - lineX2
        c = lineX2 * lineY1 - lineX1 * lineY2
        dis = (math.fabs(a*pointX+b*pointY+c)) / (math.pow(a*a+b*b,0.5))
        return dis
    
    def judge(self, pointX, pointY, pointX1, pointY1, pointX2, pointY2):
        if (pointX >= pointX1 and pointX <= pointX2) or (pointX <= pointX1 and pointX >= pointX2):
            if (pointY >= pointY1 and pointY <= pointY2) or (pointY <= pointY1 and pointY >= pointY2):
                return True
            else:
                return False
        else:
            return False

if __name__ == '__main__':
    rospy.loginfo('init')
    rospy.init_node('decision_node')
    ctrl = Controller()
    env = BattleEnv()
    tflistener = tf.TransformListener()

    # self.team_msg.robot_id = self.SELF_ID
    env.team_msg.teammate_id = 3 # 指发送队友的ID
    env.team_msg.robot_pos_x = env.robot_pose['x']
    env.team_msg.robot_pos_y = env.robot_pose['y']
    env.team_msg.robot_pjt_info = env.pjt_info

    env.team_msg.find_enemy1 = env.detection_result
    env.team_msg.enemy1_pos_x = env.ENEMY_POSE_TO_MATE['x']
    env.team_msg.enemy1_pos_y = env.ENEMY_POSE_TO_MATE['y']

    # env.team_msg.mate_supply = env.IS_SUPPLY
    env.team_msg.cmd = env.IS_SUPPLY
    env.team_msg_pub.publish(env.team_msg)

    cmdvel_slowfront = TwistControl(0.205, 0, 0, 0).Twist # 慢速向前命令
    cmdvel_slowback = TwistControl(-0.205, 0, 0, 0).Twist # 慢速向后命令
    cmdvel_slowzuotwist = TwistControl(0, 0, 0, 0.4).Twist # 慢速正转
    cmdvel_slowyoutwist = TwistControl(0, 0, 0, -0.4).Twist # 慢速反转
    cmdvel_middlefront = TwistControl(0.6, 0, 0, 0).Twist # 中速向前命令
    cmdvel_middleback = TwistControl(-0.5, 0, 0, 0).Twist # 中速向后命令
    cmdvel_fastfront = TwistControl(3.5, 0, 0, 0).Twist # 最快速向前命令
    cmdvel_fastleft = TwistControl(0, 3.5, 0, 0).Twist # 最快速向左命令
    cmdvel_stop = TwistControl(0, 0, 0, 0).Twist # 定义静止命令

    #FIXME: 
    robot_name_ = rospy.get_param("/robot_name") # O在前30秒补弹，1在后30秒补弹
    env.robot_name = (0 if (robot_name_ == "blue") else 1)
    rospy.loginfo('robot_name is {}'.format(robot_name_))
    rospy.loginfo('robot_code is {}'.format(env.robot_name))

    ctrl.chassis_mode_switch(0)
    ctrl.gimbal_mode_switch(1)

    #ctrl.cmd_fric_wheel_client(True)
    ctrl.global_path_planner_action_client.wait_for_server(rospy.Duration(0.5))
    ctrl.local_path_planner_action_client.wait_for_server(rospy.Duration(0.5))

    rospy.loginfo('Start the ICRA_RM!!!!!!')
    
    rospy.loginfo('Enter the tree')
    tree = BuildTree()  # 已经加buff进入tree
    
    rospy.spin()
