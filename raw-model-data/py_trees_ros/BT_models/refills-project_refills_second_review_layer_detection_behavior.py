from py_trees import Status, Blackboard
from refills_msgs.msg import DetectShelfLayersAction, DetectShelfLayersGoal
from py_trees_ros.actions import ActionClient


class LayerDetectionBehavior(ActionClient):
    def __init__(self, name="", action_namespace='/perception_interface/detect_shelf_layers'):
        super(LayerDetectionBehavior, self).__init__(name=name, action_spec=DetectShelfLayersAction, action_namespace=action_namespace)

#    def setup(self, timeout):
#        return super(ShelfNavigationBehavior, self).setup(timeout)

    def initialise(self):
        super(LayerDetectionBehavior, self).initialise()

        self.action_goal = DetectShelfLayersGoal()
        self.action_goal.id = Blackboard().get("current_shelf_id")

    def update(self):
        if not self.action_goal.id:
            return Status.FAILURE
        return super(LayerDetectionBehavior, self).update()

#    def terminate(self, new_status):
#        super(ShelfNavigationBehavior, self).terminate(new_status)