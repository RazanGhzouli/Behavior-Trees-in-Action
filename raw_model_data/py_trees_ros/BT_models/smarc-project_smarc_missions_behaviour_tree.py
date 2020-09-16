# Christopher Iliffe Sprague
# sprague@kth.se
# Behaviour tree that iterates 
# over a sequence of waypoints.

import py_trees_ros as ptr, py_trees as pt, rospy, json, std_msgs.msg
from behaviours import *

class BehaviourTree(ptr.trees.BehaviourTree):

    def __init__(self):

        # the blackboard
        self.bb = pt.blackboard.Blackboard()

        # data publisher
        #dp = DataPublisher()

        # safety
        s = Safe()

        # system preperation NOTE: replace
        #sp0 = Counter(10, name="System prepared?")
        #sp1 = pt.behaviours.Running(name="Preparing system!")
        #sp = pt.composites.Selector(name="System preparation", children=[sp0, sp1])

        # mission synchronisation NOTE: replace
        ms = SynchroniseMission()

        # mission execution
        me0 = AtFinalWaypoint()
        me1 = Counter(15, name="At waypoint", reset=True)
        me2 = GoTo()
        me3 = SetNextWaypoint()
        me = pt.composites.Selector(children=[me1, me2])
        me = Sequence(children=[me, me3])
        me = pt.composites.Selector(children=[me0, me])

        # mission finalisation
        self.bb.set("mission_done", False)
        mf0 = pt.blackboard.CheckBlackboardVariable(
            "Mission done?",
            variable_name="mission_done",
            expected_value=True
        )
        mf1 = Counter(20, name="At surface?")
        mf2 = pt.behaviours.Running(name="Going to surface!")
        mf3 = Counter(20, name="Payload off?")
        mf4 = pt.behaviours.Running(name="Shutting down!")
        mf = Sequence(children=[
            pt.composites.Selector(children=[mf1, mf2]),
            pt.composites.Selector(children=[mf3, mf4]),
            pt.blackboard.SetBlackboardVariable(
                name="Mission done!",
                variable_name="mission_done",
                variable_value=True
            )
        ])
        mf = pt.composites.Selector(children=[mf0, mf])

        # become behaviour tree
        tree = Sequence(children=[s, sp, ms, me, mf])
        #tree = pt.composites.Parallel(children=[dp, tree])
        super(BehaviourTree, self).__init__(tree)

        # execute the tree
        self.setup(timeout=1000)
        while not rospy.is_shutdown():
            self.tick_tock(100)

if __name__ == "__main__":

    # execute a behaviour tree with the plan
    rospy.init_node('behaviour_tree')
    try:
        BehaviourTree('betterplan.json')
    except rospy.ROSInterruptException:
        pass