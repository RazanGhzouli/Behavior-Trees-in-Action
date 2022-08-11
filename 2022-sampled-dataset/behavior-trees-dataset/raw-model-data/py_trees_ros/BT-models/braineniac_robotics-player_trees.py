#!/usr/bin/env python
import rospy
import py_trees
import py_trees_ros
import sys
import functools

from player.msg import *

class DriveRandomly(py_trees_ros.actions.ActionClient):
    def __init__(self, name="drive randomly", action_namespace="drive_randomly"):
        super(DriveRandomly, self).__init__(name, RandomDriveAction, RandomDriveGoal(), action_namespace)
        # Get the blackboard and put the obstacle and object flags into it
        self.blackboard = py_trees.blackboard.Blackboard()
        self.blackboard.obstacle_found = False
        self.blackboard.object_found = False
        self.blackboard.map_not_built = True

    def update(self):
        # Use the superclass to process the update so we don't have to
        status = super(DriveRandomly, self).update()

        # We are only interested if the status is success, because the
        # actionserver only returns that if it detects obstacle or object,
        # otherwise it is always running. Other statuses returned means that
        # something bad happened.
        if status == py_trees.common.Status.SUCCESS:
            result = self.action_client.get_result()
            if result.obstacle_found:
                self.blackboard.obstacle_found = True

        # Just pass on the status
        return status


"""
class TakePicture(py_trees_ros.actions.ActionClient):
    def __init__(self, name="take picture", action_namespace="take_picture"):
        super(TakePicture, self).__init__(name, TakePictureAction, TakePictureGoal, action_namespace)
        self.blackboard = py_trees.blackboard.Blackboard()
        self.blackboard.blurry = False

    def update(self):
        status = super(TakePicture, self).update()

        # Check the result and put the boolean value about whether or not the
        # image is blurred into the blackboard so it can be checked later
        if status == py_trees.common.Status.SUCCESS:
            result = self.action_client.get_result()
            self.blackboard.blurry = result.blurry
        
        return status
"""


def create_root():
    root = py_trees.composites.Chooser("Explorer")

    build_map_seq = py_trees.composites.Sequence("Build map Sequence")
    map_not_built = py_trees.blackboard.CheckBlackboardVariable("Map not built?",
                                                                variable_name="map_not_built",
                                                                expected_value=True,
                                                                clearing_policy=py_trees.common.ClearingPolicy.NEVER)
    map_built_flag = py_trees.blackboard.SetBlackboardVariable("map built flag off",
                                                          variable_name="map_not_built",
                                                          variable_value=False)

    build_map_goal = BuildMapGoal()
    build_map_goal.message = "build this MAP"
    build_map = py_trees_ros.actions.ActionClient("Build map", BuildMapAction, build_map_goal, "build_map")
    turn_left_msg = MoveGoal()
    turn_left_msg.direction = "ccw"
    turn_left_msg.duration = 0.5
    turn_left_msg.speed = 0.1
    turn_left = py_trees_ros.actions.ActionClient("Turn Left", MoveAction, turn_left_msg, "move")

    build_map_sel = py_trees.composites.Selector("Build map Selector")

    build_map_seq.add_child(map_not_built)
    build_map_seq.add_child(build_map_sel)
    build_map_seq.add_child(map_built_flag)
    build_map_sel.add_child(build_map)
    build_map_sel.add_child(turn_left)

    root.add_child(build_map_seq)
    # Create a sequence for the obstacle avoidance behaviour
    obs_avoid = py_trees.composites.Sequence("Avoid obstacles")
    # Check the blackboard to see if there was an obstacle found
    obstacle_found = py_trees.blackboard.CheckBlackboardVariable("obstacle found?",
                                                                 variable_name="obstacle_found",
                                                                 expected_value=True,
                                                                 clearing_policy=py_trees.common.ClearingPolicy.NEVER) # don't clear the variable
    obstacle_avoided = py_trees.blackboard.SetBlackboardVariable("obstacle flag off",
                                                                 variable_name="obstacle_found",
                                                                 variable_value=False)

    # If we want to deal differently with what happens when the robot obstacle
    # avoidance fails, then we need to do something similar to TakePicture and
    # look at the result message. At the moment there is only a "crashed"
    # result, but perhaps there could be others we want to handle differently
    avoid_obstacle = py_trees_ros.actions.ActionClient("avoid obstacle", AvoidObstacleAction, AvoidObstacleGoal, "avoid_obstacle")

    obs_avoid.add_child(obstacle_found)
    obs_avoid.add_child(avoid_obstacle)
    obs_avoid.add_child(obstacle_avoided)


    drive_randomly = DriveRandomly()

    root.add_child(obs_avoid)
    #root.add_child(object_pic)
    root.add_child(drive_randomly)

    return root

    """
    # Create a sequence for the picture taking behaviour
    object_pic = py_trees.composites.Sequence("Take picture")
    # Check the blackboard to see if there was an object found
    object_found = py_trees.blackboard.CheckBlackboardVariable("object found?",
                                                               variable_name="object_found",
                                                               expected_value=True,
                                                               clearing_policy=py_trees.common.ClearingPolicy.NEVER) # don't clear the variable
    """

    """
    # Note that this sequence is not strictly necessary - we could just put the
    # behaviours in it into the parent sequence. This is just to show that there
    # are various ways of achieving essentially the same result
    check_image = py_trees.composites.Sequence("check image")
    image_blurry = py_trees.blackboard.CheckBlackboardVariable("image ok?",
                                                               variable_name="blurry",
                                                               expected_value=False,
                                                               clearing_policy=py_trees.common.ClearingPolicy.NEVER) # don't clear the v
    got_picture = py_trees.blackboard.SetBlackboardVariable("object flag off",
                                                            variable_name="object_found",
                                                            variable_value=False)

    check_image.add_child(image_blurry)
    check_image.add_child(got_picture)

    take_picture = TakePicture()
    
    object_pic.add_child(object_found)
    object_pic.add_child(take_picture)
    object_pic.add_child(check_image)
    """

    
def shutdown(behaviour_tree):
    behaviour_tree.interrupt()

if __name__ == '__main__':
    rospy.init_node("trees")
    root = create_root()
    behaviour_tree = py_trees_ros.trees.BehaviourTree(root)
    rospy.on_shutdown(functools.partial(shutdown, behaviour_tree))
    if not behaviour_tree.setup(timeout=15):
        rospy.logerr("failed to setup the tree, aborting.")
        sys.exit(1)
    # 500ms between checks of behaviour status. Behaviours will only change
    # state during a tick
    behaviour_tree.tick_tock(500)

