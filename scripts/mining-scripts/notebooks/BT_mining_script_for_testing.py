# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 09:27:47 2021

@author: Razan
"""


import requests
import os.path
# import re
# import numpy as np
import github 
from github import Github
import pickle
# import sys
import argparse
from datetime import datetime
import pandas as pd


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
 
        
#### a function to save mined library name
def library_name():
    library = input('Enter the desired library name to use as indication in files name. Do not use space in name use either _ or camel case schema: ')
    return library







### a function to query github by entering a specific string to search on files level
def query_github(g, keywords = None):
    g= g 
    if keywords is None:
        keywords = input('Enter keyword(s)[e.g py_trees_ros, main_tree_to_execute] and file extension if needed. Separate using comma: ')
    else:
        keywords = keywords
    keywords = [keyword.strip() for keyword in keywords.split(',')]
    print("Start query." )
    if keywords[1] is None:
         query = f'"{keywords}" in:file'
    else: 
        query = f'"{keywords[0]}" in:file extension:{keywords[1]}'
        
    result = g.search_code(query, order='desc')
    print("------------------------------------------------------------------------------")
    print("Query finished.")
    print(f'Found {result.totalCount} file(s)')
    print("------------------------------------------------------------------------------")

    return result 


### a function to extract found files urls and repos names and save for later use in pickle format
def extract_url_repoName(result, library, date):
    # result = result
    new_repo = {}
    print("Start extracting found files URL and repos names." )
    for file in result:
        url = file.download_url 

        #repo_name = file.repository.full_name.replace('/','_')
        repo_name = file.repository.full_name
    
        if repo_name in new_repo:
        ### append the new url to the existing array at this slot
            new_repo[repo_name].append(url)
        else:
        ### create a new array in this slot
            new_repo[repo_name] = [url]
  
    ### saving the found results 
    f = open( date+ "_" + library + "_repoName_plus_URL_"+ ".pkl","wb")   
    pickle.dump(new_repo,f)
    f.close()  
    print("A file containing repos names and files URL was saved to your working directory")
    print("------------------------------------------------------------------------------")
    print("The number of repository: {}".format(len(new_repo)))
    print("The number of files: {}".format(sum(len(dct) for dct in new_repo.values() )))
    print("------------------------------------------------------------------------------")
    
    return new_repo

# #### uncomment this part and related part in main if you want to limit number of returned results
# def limit_result_size(result, desired_size):    
#     max_size = desired_size  
#     if result.totalCount >= max_size:
#         print(f'The number of mined GitHub files is {result.totalCount} and it was limmited to {max_size} ')
#         return result[:max_size]


### extract repo name, html link, las commit sha

def extract_repolink_name_sha(g,result,library,date):
    repo_name_html_sha = {}
    print("Start extracting found repos GitHub html links and last sha number." )
    for file in result:
        repo_name = file.repository.full_name
        if repo_name not in repo_name_html_sha:
            repo_html = file.repository.html_url        
            commits = g.get_repo(file.repository.full_name).get_commits()
            repo_name_html_sha[repo_name] = {}
            repo_name_html_sha[repo_name][repo_html] =  commits[0].commit.sha 
            
    print("Finished extracting found repos GitHub html links and last sha number." )

    ## insert them to daraframe
    repo_name =[]
    repo_name = [key for key, value in repo_name_html_sha.items()]
    repo_html = []
    repo_html = [k for value in repo_name_html_sha.values() for k in value.keys() ]
    repo_sha = []
    repo_sha = [v for value in repo_name_html_sha.values() for v in value.values() ]
    
    columns_name = ['name' , 'html_link' , 'sha']
    repo_df = pd.DataFrame(columns = columns_name)
    repo_df['name'] = repo_name
    repo_df['html_link'] = repo_html
    repo_df['sha'] = repo_sha
    
    ### Save the extracted info to excel
    repo_df.to_csv(date + "_"+ library +"_RepoProjectNameHtmlSha_csv.csv")
    print("A file containing repos GitHub html links and last sha number was saved to your working directory")
    print("------------------------------------------------------------------------------")
    
    


#### a function to specify save path location for downloaded files
def save_path():
    savePath = input('Enter the desired save path for downloading the found files: ')
    return savePath

### a function to download found files content   
def download_models(savePath, url_repo_name_dict,repoName_html_sha):
    file_count = 0
    
    print("Start downloading found files." )
    for key,value in url_repo_name_dict.items():
        
        ###getting the sha number for the specific commit point in repo where the mining was done earlier
        sha_index = repoName_html_sha.index[repoName_html_sha['name'] == key]
        sha = {'tree' : repoName_html_sha.sha[sha_index][0] }
        
        ####download the file content at specific point in the repo
        for i in range(len(value)):
            r = requests.get(value[i],sha)
            ### if you want to change the path where files are saved change  "/home/jovyan/src/notebooks/downloads/pytreeros" to where you want, also for XML fromat files change the re.search to xml instead of py 
            # open(os.path.join(savePath, os.path.basename(key.replace('/','_')+'_'+(re.search('/(\w*((%20\w)*)?.py)', value[i]).group(1)))) , "wb").write(r.content)
            open(os.path.join(savePath, os.path.basename(key.replace('/','_')+'_'+value.split("/")[-1])) , "wb").write(r.content)

            file_count += 1
    print("Finished downloading found files." )
    print("------------------------------------------------------------------------------")
    print("Download complete for {} files".format(file_count))
    print("------------------------------------------------------------------------------")
    
    


def init_argparse() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(

        # usage="%(prog)s [OPTION] [FILE]...",

        description="pass arguments for access token, query string and save path"

    )

    parser.add_argument(

        "-ac", "--accesstoken", required=False

    )
    
    parser.add_argument(

        "-q", "--query", required=False

    )
    
    parser.add_argument(

        "-p", "--savePath", required=False
        

    )

    return parser

    

def main(accesstoken =None , query = None, savePath = None):
    
    
    
    ### access token and query Github 
    if accesstoken != None:
        token = accesstoken
        g = access_token(token)
    
        result = query_github(g, keywords = query)
    else:
        token = input("Enter your Github access token: ")
        g = access_token(token)
           
        result = query_github(g,keywords= None)
    
    ### for later file naming enter the mined library name
    library = library_name()
    
    ### today's date for later saved file formating
    date = datetime.today().strftime('%d%m%Y') 
    ### change here depending on number of files that you want to download. GitHub API has a limit of maximum 1000 files
    # desired_size = 1000
    # result = limit_result_size(result, desired_size) 
   
    ### extract found files url and repos names
    url_repo_name_dict= extract_url_repoName(result,library,date)
    
    ### extract found repos name, sha and html link 
    repoName_html_sha = extract_repolink_name_sha(g,result,library,date)
    
    ### save found files path
    if savePath != None:
        ### download the found files
        download_models(savePath, url_repo_name_dict, repoName_html_sha)
    else:
        ### enter save path
        # savePath = "C:/Users/Razan/Behavior-Trees-in-Action/scripts/notebooks/models/"
        savePath = save_path()
         ### download the found files
        download_models(savePath, url_repo_name_dict, repoName_html_sha)
        
    
    
    

if __name__ == '__main__':
    parser = init_argparse()

    args = parser.parse_args()
    
    main(accesstoken = args.accesstoken , query= args.query, savePath = args.savePath)
    



