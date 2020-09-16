from py_trees import Status, Blackboard
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from py_trees_ros.actions import ActionClient


class BaseNavigationBehavior(ActionClient):
    def __init__(self, name="", move_base_action_name='nav_pcontroller/move_base'):
        super(BaseNavigationBehavior, self).__init__(name=name, action_spec=MoveBaseAction, action_namespace=move_base_action_name)

#    def setup(self, timeout):
#        return super(ShelfNavigationBehavior, self).setup(timeout)

    def initialise(self):
        super(BaseNavigationBehavior, self).initialise()
        self.read_action_goal()

    def update(self):
        if not self.action_goal.target_pose:
            return Status.FAILURE
        return super(BaseNavigationBehavior, self).update()

#    def terminate(self, new_status):
#        super(ShelfNavigationBehavior, self).terminate(new_status)

    def read_action_goal(self):
        self.action_goal = MoveBaseGoal()
        self.action_goal.target_pose = Blackboard().get("move_base_target_pose")
