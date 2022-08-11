from py_trees import Status, Blackboard
from control_msgs.msg import FollowJointTrajectoryAction, FollowJointTrajectoryGoal
from py_trees_ros.actions import ActionClient


class ArmMovementBehavior(ActionClient):
    def __init__(self, name="", action_namespace='/whole_body_controller/follow_joint_trajectory'):
        super(ArmMovementBehavior, self).__init__(name=name, action_spec=FollowJointTrajectoryAction, action_namespace=action_namespace)

#    def setup(self, timeout):
#        return super(ShelfNavigationBehavior, self).setup(timeout)

    def initialise(self):
        super(ArmMovementBehavior, self).initialise()
        self.action_goal = FollowJointTrajectoryGoal()
        self.action_goal.trajectory = Blackboard().get("arm_trajectory")

    def update(self):
        if not self.action_goal.trajectory:
            return Status.FAILURE
        return super(ArmMovementBehavior, self).update()

#    def terminate(self, new_status):
#        super(ShelfNavigationBehavior, self).terminate(new_status)

