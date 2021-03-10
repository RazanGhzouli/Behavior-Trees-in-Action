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
from unittest.mock import patch
import os
import re
   

    

class MockGithubResponse(unittest.TestCase):

        
    def testAccessTokenWorking(self):
        """
        Test access token function work
        """
        access_token = BT_mining_script_for_testing.access_token
        
        ### you should add a working token here to test 
        data = ['be505053a366341d36704f843e3f2a6e056774e5']
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
        
        
    @patch('builtins.input', return_value='py_trees_ros')
    def testQueryGithubInput(self, input):
        """
        Test query function catch entered input
        """
        
        query_github = BT_mining_script_for_testing.query_github
               
        data = ['be505053a366341d36704f843e3f2a6e056774e5'] 
        g = Github(data[0])
        
        self.assertIsNotNone(
            query_github(g), "input wasn't catched by function")
    
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def testNumberReturnedFiles (self, mock_stdout):
        """
        Test query function return specific number of files
        
        """
        query_github = BT_mining_script_for_testing.query_github
               
        data = ['be505053a366341d36704f843e3f2a6e056774e5'] 
        g = Github(data[0])
        expected_output = "Found 258 file(s)\n"
        
        query_github(g ,keywords = "py_trees_ros")
        self.assertEqual(mock_stdout.getvalue(), expected_output, "Number of files differ from the paper based results")
        
    
        
    def testFileWriting(self):
        """
        Test extract_url_repo_name function return non-empty dictionary of  URL and repo names
        """
        query_github = BT_mining_script_for_testing.query_github
        extract_url_repo_name = BT_mining_script_for_testing.extract_url_repo_name
               
        data = ['be505053a366341d36704f843e3f2a6e056774e5'] 
        g = Github(data[0])
        result = query_github(g ,keywords = "py_trees_ros")
        
        self.assertTrue(extract_url_repo_name(result),"function returned empty dictionary")
        

        
    
        

if __name__ == '__main__':
    unittest.main()
    print("Everything passed")
    
    
    





