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
            result, "access token is not valid, change the token in the code to working one")
        
        
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def testAccessTokenErrorCatch(self, mock_stdout):
        """
        Test access token function catch error with token value
        """
        access_token = BT_mining_script_for_testing.access_token
        
        data = ['12345678932165498774185296332145987555']
        expected_output = "Please provide a working access token\n"

        access_token(data[0])             
        self.assertEqual(mock_stdout.getvalue(), expected_output, "another type of error not related to access token ")

        
    
        

if __name__ == '__main__':
    unittest.main()
    print("Everything passed")
    
    
    





