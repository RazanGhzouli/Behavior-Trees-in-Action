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
import sys
import argparse 

    

class MockGithubResponse(unittest.TestCase):
    ## fake access token. In case access token not passed in cmd, add a working one here
    data = '12345678932165498774185296332145987555'

        
    def testAccessTokenWorking(self):
        """
        Test access token function work
        """
        access_token = BT_mining_script_for_testing.access_token
        

        result = access_token(self.data)

        self.assertIsNotNone(
            result, "access token is not valid, change the token in the code to working one")
        
        
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def testAccessTokenErrorCatch(self, mock_stdout):
        """
        Test access token function catch error with token value
        """
        access_token = BT_mining_script_for_testing.access_token
        
        ## fake access token
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
               
        g = Github(self.data)
        
        self.assertIsNotNone(
            query_github(g), "input wasn't catched by function")
    
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def testNumberReturnedFiles (self, mock_stdout):
        """
        Test query function return specific number of files
        
        """
        query_github = BT_mining_script_for_testing.query_github
               
        g = Github(self.data)
        expected_output = "Found 254 file(s)\n"
        
        query_github(g ,keywords = "py_trees_ros")
        self.assertEqual(mock_stdout.getvalue(), expected_output, "Number of files differ from the paper based results")
        
    
        
    def testFileWriting(self):
        """
        Test extract_url_repo_name function return non-empty dictionary of  URL and repo names
        """
        query_github = BT_mining_script_for_testing.query_github
        extract_url_repo_name = BT_mining_script_for_testing.extract_url_repo_name
               
        g = Github(self.data)
        result = query_github(g ,keywords = "py_trees_ros")
        
        self.assertTrue(extract_url_repo_name(result),"function returned empty dictionary")
        
    
    def testSlicedResultSize(self):
        """
        Test limit_result_size function return the desired result size
        """
        query_github = BT_mining_script_for_testing.query_github
        limit_result_size = BT_mining_script_for_testing.limit_result_size
               
        desired_size = 10
        g = Github(self.data)
        result = query_github(g ,keywords = "py_trees_ros")
        self.assertEqual(len(list(limit_result_size(result,desired_size))), desired_size, "the limit_result_size function did not slice the result size")

    
    def testLimitSizeReturnedValue(self):
        """
        Test limit_result_size function does return results
        """
        query_github = BT_mining_script_for_testing.query_github
        limit_result_size = BT_mining_script_for_testing.limit_result_size
               
        desired_size = 10
        g = Github(self.data)
        result = query_github(g ,keywords = "py_trees_ros")
        self.assertTrue(limit_result_size(result,desired_size), "function returned empty result")
    
    
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)       
    def testDownloadFiles (self, mock_stdout):
        """
        Test download_models download files
        
        """
        query_github = BT_mining_script_for_testing.query_github
        limit_result_size = BT_mining_script_for_testing.limit_result_size
        extract_url_repo_name = BT_mining_script_for_testing.extract_url_repo_name
        download_models = BT_mining_script_for_testing.download_models
               
        desired_size = 2
        g = Github(self.data)
        result = extract_url_repo_name(limit_result_size(query_github(g ,keywords = "py_trees_ros"),desired_size))
        expected_output = "Download complete for 2 files\n"
        
        download_models(os.getcwd(),result)  
        self.assertEqual((re.search( "(Download complete for 2 files\n)", mock_stdout.getvalue()).group(1)), expected_output, "Files were not downloaded")    
    
    
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)       
    def testSaveDictionary (self, mock_stdout):
        """
        Test extract_url_repo_name save dictionary with repo and url names
        
        """
        query_github = BT_mining_script_for_testing.query_github
        limit_result_size = BT_mining_script_for_testing.limit_result_size
        extract_url_repo_name = BT_mining_script_for_testing.extract_url_repo_name
               
        desired_size = 2
        g = Github(self.data)

        expected_output = "A file containing repo name and files URL was saved to your working directory\n"
        extract_url_repo_name(limit_result_size(query_github(g ,keywords = "py_trees_ros"),desired_size))
        self.assertEqual((re.search( "(A file containing repo name and files URL was saved to your working directory\n)", mock_stdout.getvalue()).group(1)), expected_output, "Dictionary was not saved")
      
        
      
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)       
    def testNumberRepo (self, mock_stdout):
        """
        Test extract_url_repo_name find specific number of repo
        
        """
        query_github = BT_mining_script_for_testing.query_github
        limit_result_size = BT_mining_script_for_testing.limit_result_size
        extract_url_repo_name = BT_mining_script_for_testing.extract_url_repo_name
               
        desired_size = 2
        g = Github(self.data)

        expected_output = "The number of repository: 2\n"
        extract_url_repo_name(limit_result_size(query_github(g ,keywords = "py_trees_ros"),desired_size))
        self.assertEqual((re.search( "(The number of repository: 2\n)", mock_stdout.getvalue()).group(1)), expected_output, "Number of repo is not similar to study")
    
        


if __name__ == '__main__':

    if len(sys.argv) >= 1:
    
        MockGithubResponse.data = sys.argv.pop()
        
    unittest.main()
    print("Everything passed")
    
    
    





