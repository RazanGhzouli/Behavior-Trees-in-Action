#!/usr/bin/env python
# coding: utf-8

# In[1]:


# from testbook import testbook

import unittest
import BT_mining_script_for_testing
import mock
import io
import unittest.mock
from github import Github


    

    

class MockGithubResponse(unittest.TestCase):

        
    def testAccessTokenWorking(self):
        """
        Test access token function work
        """
        access_token = BT_mining_script_for_testing.access_token
        
        ### you should add a working token here to test 
        data = ['16b16fdd48defe39cf97e64812805254b3a5584d']
        result = access_token(data[0])

        self.assertIsNotNone(
            result, "access token is not valid")

        
    
        

if __name__ == '__main__':
    unittest.main()
    print("Everything passed")
    
    
    





