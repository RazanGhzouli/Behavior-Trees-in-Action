# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 09:27:47 2021

@author: Razan
"""


import os.path
import requests
import os.path
import re
import numpy as np
import github 
from github import Github
import pickle
import sys
import argparse

def access_token(token):
    ACCESS_TOKEN = token ## enter your githun token
    g = Github(ACCESS_TOKEN)
    
    try:
        repo = g.get_repo("PyGithub/PyGithub")
        if repo.full_name == "PyGithub/PyGithub":
#         print(repo.full_name)#
            print("Access token works")
            return g
    except github.GithubException as e:
        
        if (e.data['message']=='Bad credentials'):
            print("Please provide a working access token")
        else:
            print (e)
        
## a function to query github by entering a specific string to search on files level
def query_github(g, keywords = None):
    g= g 
    if keywords is None:
        keywords = input('Enter keyword(s)[e.g py_trees_ros, main_tree_to_execute]: ')
    else:
        keywords = keywords
    keywords = [keyword.strip() for keyword in keywords.split(',')]
    query = f'"{keywords}" in:file extension:py' ### change extension to XML for "main_tree_to_execute"
    result = g.search_code(query, order='desc')
    print(f'Found {result.totalCount} file(s)')
    return result 


def extract_url_repo_name(result):
    # result = result
    new_repo = {}
    for file in result:
        url = file.download_url 

        repo_name = file.repository.full_name.replace('/','_')
    
        if repo_name in new_repo:
        # append the new url to the existing array at this slot
            new_repo[repo_name].append(url)
        else:
        # create a new array in this slot
            new_repo[repo_name] = [url]
            
    f = open("repo_name_plus_URL.pkl","wb")
    pickle.dump(new_repo,f)
    f.close()  
    print("A file containing repo name and files URL was saved to your working directory")
    print("------------------------------------------------------------------------------")
    print("The number of repository: {}".format(len(new_repo)))
    print("The number of files: {}".format(sum(len(dct) for dct in new_repo.values() )))
    
    return new_repo


def limit_result_size(result, desired_size):    
    max_size = desired_size  
    if result.totalCount >= max_size:
        print(f'The number of mined GitHub files is {result.totalCount} and it was limmited to {max_size} ')
        return result[:max_size]

## remeber to call this function    
def download_models(save_path, url_repo_name_dict):
    file_count = 0
    for key,value in url_repo_name_dict.items():
        for i in range(len(value)):
            r = requests.get(value[i])
            ## if you want to change the path where files are saved change  "/home/jovyan/src/notebooks/downloads/pytreeros" to where you want, also for XML fromat files change the re.search to xml instead of py 
            open(os.path.join(save_path, os.path.basename(key+'_'+(re.search('/(\w*((%20\w)*)?.py)', value[i]).group(1)))) , "wb").write(r.content)
            file_count += 1

    print("Download complete for {} files".format(file_count))

def init_argparse() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(

        # usage="%(prog)s [OPTION] [FILE]...",

        description="pass arguments for access token and query string"

    )

    parser.add_argument(

        "-ac", "--accesstoken", required=False

    )
    
    parser.add_argument(

        "-q", "--query", required=False

    )

    return parser

    

def main(accesstoken =None , query = None):
    save_path = "C:/Users/Razan/Behavior-Trees-in-Action/scripts/notebooks/models/"
    
    if accesstoken != None:
        token = accesstoken
        g = access_token(token)
    
        result = query_github(g, keywords = query)
    else:
        token = input("Enter your Github access token: ")
        g = access_token(token)
           
        result = query_github(g,keywords= None)
    
    ## change here depending on number of files that you want to download. GitHub API has a limit of maximum 1000 files
    desired_size = 100
    result = limit_result_size(result, desired_size) 
   
    url_repo_name_dict= extract_url_repo_name(result)
    
    download_models(save_path, url_repo_name_dict)
    

if __name__ == '__main__':
    parser = init_argparse()

    args = parser.parse_args()
    
    main(accesstoken = args.accesstoken , query= args.query)
    



