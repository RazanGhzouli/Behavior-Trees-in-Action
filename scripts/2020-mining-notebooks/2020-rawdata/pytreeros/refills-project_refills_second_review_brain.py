#!/usr/bin/env python
## https://github.com/refills-project/refills_second_review/blob/master/nodes/brain
import functools
import rospy

from py_trees import Blackboard, BehaviourTree, Selector, Sequence, Status
from py_trees.display import render_dot_tree, ascii_tree
from py_trees.meta import running_is_success
from py_trees.visitors import SnapshotVisitor

from refills_second_review.arm_movement_behavior import ArmMovementBehavior
from refills_second_review.base_navigation_behavior import BaseNavigationBehavior
from refills_second_review.configure_layer_detection_behavior import ConfigureLayerDetectionBehavior
from refills_second_review.finish_perception_behavior import FinishPerceptionBehavior
from refills_second_review.layer_detection_behavior import LayerDetectionBehavior


def cram_plan(debug):
    my_blackboard = Blackboard()
    my_blackboard.set("current_shelf_id", "http://knowrob.org/kb/dm-market.owl#DMShelfW100_XLUZQHSE")

    layer_detection = Sequence('layer detection composite')
    layer_detection.add_child(ConfigureLayerDetectionBehavior('configure layer detection'))
    layer_detection.add_child(BaseNavigationBehavior('move base'))
    layer_detection.add_child(running_is_success(LayerDetectionBehavior)('layer detection'))
    layer_detection.add_child(ArmMovementBehavior('move arm'))
    layer_detection.add_child(FinishPerceptionBehavior('finish perception'))

    root = Sequence('root')
    root.add_child(layer_detection)

    tree = BehaviourTree(root)

    if debug:
        # TODO create data folder if it does not exist
        def post_tick(snapshot_visitor, behaviour_tree):
            print(u'\n' + ascii_tree(behaviour_tree.root, snapshot_information=snapshot_visitor))

        snapshot_visitor = SnapshotVisitor()
        tree.add_post_tick_handler(functools.partial(post_tick, snapshot_visitor))
        tree.visitors.append(snapshot_visitor)
        render_dot_tree(root, name='tree')

    tree.setup(3)
    return tree

if __name__ == '__main__':
    rospy.init_node('brain')
    debug = True
    if debug:
        tree_tick_rate = 2000
    else:
        tree_tick_rate = 20
    tree = cram_plan(debug)
    print('interface running')
    while not rospy.is_shutdown() and tree.root.status != Status.SUCCESS:
        try:
            tree.tick()
            rospy.sleep(tree_tick_rate/1000)
        except KeyboardInterrupt:
            break