#!/usr/bin/python
'''
States for state machine of rocky executive layer

'''

import roslib

import time
import random

import smach, smach_ros
import rospy

class Egress(smach.State):
  '''
  exit the starting platform
  '''
  def __init__(self):
    smach.State.__init__(self, outcomes=['succeeded', 'aborted'])
    pass

  def execute(self, userdata):
    if random.getrandbits(1):
      return 'succeeded'
    else:
      return 'aborted'

class Ingress(smach.State):
  '''
  enter the starting platform
  '''
  def __init__(self):
    smach.State.__init__(self, outcomes=['succeeded', 'aborted'])
    pass

  def execute(self, userdata):
    if random.getrandbits(1):
      return 'succeeded'
    else:
      return 'aborted'

class Transit(smach.State):
  '''
  move from one location to another using slam and navigation
  '''
  def __init__(self):
    smach.State.__init__(self, outcomes=['succeeded', 'aborted'])
    pass

  def execute(self, userdata):
    if random.getrandbits(1):
      return 'succeeded'
    else:
      return 'aborted'

class SearchForPreCached(smach.State):
  '''
  perform search using given search pattern for pre-cached sample
  '''
  def __init__(self):
    smach.State.__init__(self, outcomes=['succeeded', 'aborted'])
    pass

  def execute(self, userdata):
    if random.getrandbits(1):
      return 'succeeded'
    else:
      return 'aborted'

class Search(smach.State):
  '''
  basic search state
  '''
  def __init__(self):
    smach.State.__init__(self, outcomes=['succeeded', 'aborted'])
    pass

  def execute(self, userdata):
    if random.getrandbits(1):
      return 'succeeded'
    else:
      return 'aborted'

class RecognizeSample(smach.State):
  '''
  attempt to recognize and classify sample at close range
  '''
  def __init__(self):
    smach.State.__init__(self, outcomes=['succeeded', 'aborted'])
    pass

  def execute(self, userdata):
    if random.getrandbits(1):
      return 'succeeded'
    else:
      return 'aborted'

class RetrieveSample(smach.State):
  '''
  pick up the sample
  '''
  def __init__(self):
    smach.State.__init__(self, outcomes=['succeeded', 'aborted'])
    pass

  def execute(self, userdata):
    if random.getrandbits(1):
      return 'succeeded'
    else:
      return 'aborted'

if __name__ == '__main__':
  random.seed()

  sm = smach.StateMachine(outcomes=['done', 'dead'])
  with sm:
    smach.StateMachine.add('EGRESS', Egress(),
        transitions={'succeeded':'INGRESS',
                     'aborted':'EGRESS'})
    smach.StateMachine.add('INGRESS', Ingress(),
        transitions={'succeeded':'done',
                     'aborted':'INGRESS'})

  rospy.init_node('state_machine')
  sm.set_initial_state(['EGRESS'])
  sis = smach_ros.IntrospectionServer('name', sm, '/SM_ROOT')
  sis.start()
  outcome = sm.execute()
  sis.stop()
